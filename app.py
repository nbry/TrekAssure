import os
import requests
from flask import Flask, render_template, redirect, session, flash, g, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message
from email_validator import validate_email, EmailNotValidError

from forms import TrailSearchForm, UserSignupForm, LoginForm, SecureHikeForm, Forgot
from models import db, connect_db, User, TrailsSearch, SecuredHikePamphlet
# from secrets import m_key, h_key, t_pass
from functions import (search_for_trails, get_trail, get_conditions,
                       get_geo_info, rate_difficulty, get_directions, search_for_nearest,
                       secure_trip)

CURR_USER_KEY = "curr_user"
SEARCH_ID = "SEARCH_ID"
PAMPHLET_ID = "PAMPHLET_ID"
m_key = os.environ.get('m_key', None)
h_key = os.environ.get('h_key', None)
t_pass = os.environ.get('t_pass', None)


app = Flask(__name__)
MQAPI_BASE_URL = 'http://www.mapquestapi.com/'
HPAPI_BASE_URL = 'https://www.hikingproject.com/data'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='TrekAssure@gmail.com',
    MAIL_PASSWORD=t_pass
)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///trekassure_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', "EIJALWIEJAEFIJ320F23F8SEF209238FDI")
toolbar = DebugToolbarExtension(app)

connect_db(app)

# *****************************
# LOGIN/, LOGOUT, AND g FUNCTIONS
# *****************************


@app.before_request
def handle_g_data():
    """ Handling of stored data for a user's session """

    # store user in g
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

    # store their last trail search in g
    if SEARCH_ID in session:
        g.search = TrailsSearch.query.get(session[SEARCH_ID])
    else:
        g.search = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user. Clear session"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    if SEARCH_ID in session:
        del session[SEARCH_ID]

    if PAMPHLET_ID in session:
        del session[PAMPHLET_ID]


@app.route('/')
def home_page():
    """ Show Home Page """
    return render_template("home.html")

# *****************************
# TREKASSURE "TRAIL SEARCH" DATA REQUEST HANDLING
# *****************************


@app.route('/trails/results')
def get_trails():
    """ Handle a request (from front end) and respond with
    a JSON object with trail info """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    place_search = request.args['place']
    radius = int(request.args['radius'])
    geo_info = get_geo_info(m_key, place_search)

    results = search_for_trails(h_key, geo_info['lat'],
                                geo_info['lng'], radius)
    for trail in results:
        trail['difficulty'] = rate_difficulty(trail['difficulty'])

    return jsonify(results)


@app.route('/trails/store-results', methods=['POST'])
def store_trails():
    """ Store JSON results to database """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    response = request.get_json()

    results = response['data']['results']
    place = response['data']['place']
    radius = response['data']['radius']

    results_to_db = TrailsSearch(
        user_id=g.user.id,
        place=place,
        radius=radius,
        data=results)

    db.session.add(results_to_db)
    db.session.commit()

    search_id = results_to_db.id
    session['SEARCH_ID'] = search_id

    return jsonify(results_to_db.data)


# *****************************
# "TRAIL SEARCH" ROUTES
# *****************************

@app.route('/trails/search')
def show_search_results():
    """ Render a form that shows "Find Your Trail" form """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    session['unlocked'] = True

    form_t = TrailSearchForm()
    form_s = SecureHikeForm()

    if SEARCH_ID in session:
        if g.search:
            return render_template("/trail/search_form.html", form_t=form_t, form_s=form_s, results=g.search.data)
        else:
            return render_template("/trail/search_form.html", form_t=form_t, form_s=form_s, results=None)

    else:
        return render_template("/trail/search_form.html", form_t=form_t, form_s=form_s, results=None)


@app.route('/trails/<int:trail_id>')
def show_trail(trail_id):
    """ Render a page that shows detail about a trail, should the user manually search by id.
    This route is not an explicit feature of TrekAssure. It's more of a quality of life consideration """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    session['unlocked'] = True

    try:
        trail = get_trail(h_key, trail_id)
        trail['difficulty'] = rate_difficulty(trail['difficulty'])
        if trail['imgMedium'] == "":
            trail['imgMedium'] = "/static/images/no-image.png"

        form_s = SecureHikeForm()

        return render_template('/trail/trail_info.html', result=trail, form_s=form_s)

    except:
        flash("Trail not found", "danger")
        return redirect('/trails/search')

# *****************************
# "SECURED HIKE PAMPHLET" ROUTES
# *****************************


@app.route('/trails/<int:trail_id>/secure', methods=['GET', 'POST'])
def secure_hike(trail_id):
    """ Process the POST route for securing a trial. Trail ID should be
    captured on a click event written in javascript. If User made a search
    recently, they can refresh the page """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    form_s = SecureHikeForm()

    if form_s.validate_on_submit():
        home_address = form_s.home_address.data
        trail = get_trail(h_key, trail_id)
        secured_trip = secure_trip(m_key, trail, home_address)

        pamphlet_to_db = SecuredHikePamphlet(
            user_id=g.user.id,
            home_destination=home_address,
            trail_id=trail_id,
            data=secured_trip
        )
        db.session.add(pamphlet_to_db)
        db.session.commit()

        flash("Success!", "success")
        return redirect(f'/users/{g.user.id}/pamphlets/{pamphlet_to_db.id}')

    else:
        form_t = TrailSearchForm()
        return render_template('/trail/search_form.html', form_t=form_t, form_s=form_s, trail_id=trail_id)


# *****************************
# USER PAMPHLET ROUTES
# *****************************

@app.route('/users/<int:user_id>/pamphlets/<int:pamphlet_id>')
def show_secured_hike_pamphlet(user_id, pamphlet_id):
    """ Route that shows saved user pamphlets. If session user does not match user_id,
    then redirect back to trail route. """

    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect("/trails/search")

    pamphlet = SecuredHikePamphlet.query.get_or_404(pamphlet_id)

    if pamphlet.user.id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect("/trails/search")

    secured_trip = pamphlet.data
    trail = get_trail(h_key, pamphlet.trail_id)
    session[PAMPHLET_ID] = pamphlet_id

    return render_template('/trail/secure_results.html', secured_trip=secured_trip, trail=trail, pamphlet_id=pamphlet_id)


@app.route('/users/<int:user_id>/pamphlets/<int:pamphlet_id>/send')
def send_pamphlet_email(user_id, pamphlet_id):
    """ Send email to user. Receives raw text data from javascript files to render email"""
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect("/trails/search")

    if pamphlet_id != session['PAMPHLET_ID']:
        flash("Please view pamphlet before sending", "warning")
        return redirect("/trails/search")

    try:
        to_email = request.args['email']
        valid = validate_email(to_email, allow_smtputf8=False)

        mail = Mail(app)
        msg = Message("Your Pamphlet", sender="TrekAssure@gmail.com",
                      recipients=[to_email])
        msg.body = (request.args['pamphletText']
                    + "\n"
                    + f"This email was sent by {g.user.email} using TrekAssure")
        mail.send(msg)
        return "Sent Email!"

    except:
        return "Invalid Email Address"


@app.route('/users/<int:user_id>/pamphlets')
def redirect_to_account_info(user_id):
    """ Show user all pamphlets they created """

    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect(f"/users/{g.user.id}")

    user = User.query.get(user_id)

    return render_template("/user/pamphlets.html", user=user)


@app.route('/users/<int:user_id>/pamphlets/<int:pamphlet_id>/delete')
def delete_pamphlet(user_id, pamphlet_id):
    """ Delete a single pamphlet """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    pamphlet = SecuredHikePamphlet.query.get(pamphlet_id)
    try:
        db.session.delete(pamphlet)
        db.session.commit()

        flash("Deleted!", "success")
        return redirect(f'/users/{user_id}/pamphlets')

    except:
        flash("Something went wrong", "danger")
        return redirect(f'/users/{user_id}/pamphlets')


@app.route('/users/<int:user_id>/pamphlets/delete', methods=["POST"])
def delete_all_pamphlets(user_id):
    """ Delete All Pamphlets """

    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect(f"/users/{g.user.id}")

    user_pamphlets = db.session.query(
        SecuredHikePamphlet).filter_by(user_id=user_id).all()

    try:
        for pamphlet in user_pamphlets:
            db.session.delete(pamphlet)
            db.session.commit()

        flash("Deleted Everything!", "success")
        return redirect(f'/users/{user_id}/pamphlets')

    except:
        flash("Something went wrong", "danger")
        return redirect(f'/users/{user_id}/pamphlets')


# *****************************
# USER ACCOUNT ROUTES
# *****************************


@app.route('/users/<int:user_id>')
def show_user_profile(user_id):
    """ Show user profile. If session user does not match user_id, redirect to trail route """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect(f"/users/{g.user.id}")

    session['unlocked'] = True

    user_info = User.query.get(g.user.id)
    form = UserSignupForm()
    form_categories = form.data
    del form_categories['csrf_token']

    form_cats = [k for k in form_categories]

    return render_template('/user/profile.html', user=user_info, form=form, form_cats=form_cats)


@app.route('/users/<int:user_id>/update', methods=["POST"])
def update_user_settings(user_id):
    """ Handle user request to change account settings """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect(f"/users/{g.user.id}")

    form = UserSignupForm()

    if form.validate_on_submit():
        try:
            data = form.data
            user = User.query.get(user_id)
            if not User.authenticate(user.username, data['password']):
                flash("Incorrect Password", "warning")
                return redirect(f'/users/{user_id}')

            user.username = data['username']
            user.email = data['email']
            user.address = data['address']

            if data['new_password'] != "":
                if len(data['new_password']) < 6:
                    flash("password must at least 6 characters", "warning")
                    return redirect(f'/users/{user_id}')
                else:
                    user.password = User.hash_pass(data['new_password'])

            db.session.commit()

            flash(f"Updated!", "success")
            return redirect(f'/users/{user_id}')

        except:
            if IntegrityError:
                flash(f"Username {data['username']} already exists", "danger")
                return redirect(f'/users/{user_id}')

    else:
        for error in form.errors:
            flash(form.errors[error][0], "danger")
        return redirect(f'/users/{user_id}')


@app.route('/users/<int:user_id>/history')
def view_search_history(user_id):
    """ View user search_history """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect(f"/users/{g.user.id}")

    user = User.query.get(user_id)
    return render_template("/user/search-his.html", user=user)


@app.route('/users/<int:user_id>/history/delete', methods=["POST"])
def delete_search_history(user_id):
    """ Delete user search history """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect(f"/users/{g.user.id}")

    search_history = db.session.query(
        TrailsSearch).filter_by(user_id=user_id).all()

    try:
        for search in search_history:
            db.session.delete(search)
            db.session.commit()

        flash("Deleted History!", "success")
        return redirect(f'/users/{user_id}/history')

    except:
        flash("Something went wrong", "danger")
        return redirect(f'/users/{user_id}/history')


@app.route("/users/<int:user_id>/delete", methods=['POST'])
def delete_user(user_id):
    """ Delete a user """
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect(f"/users/{g.user.id}")

    user = db.session.query(User).filter_by(id=user_id).first()
    searches = db.session.query(TrailsSearch).filter_by(user_id=user_id).all()
    pamphlets = db.session.query(
        SecuredHikePamphlet).filter_by(user_id=user_id).all()

    try:
        for search in searches:
            db.session.delete(search)
        for pamphlet in pamphlets:
            db.session.delete(pamphlet)
        db.session.delete(user)
        db.session.commit()

        do_logout()
        flash("Deleted Account!", "success")
        return redirect('/')

    except:
        flash("Something went wrong", "danger")
        return redirect(f'/users/{user_id}')


@app.route('/users')
def redirect_to_user_profile():
    """ Redirect to session user profile """

    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    return redirect(f'/users/{g.user.id}')


@app.route('/signup', methods=['GET', 'POST'])
def signup_user():
    """ Show sign up page for a user, and handle post """

    form = UserSignupForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if form.email.data == "":
            email = None
        else:
            email = form.email.data

        if form.address.data == "":
            address = None
        else:
            address = form.address.data

        new_user = User.register(username, password, email, address)
        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if User.query.filter_by(username=username).first():
                form.username.errors.append('Username taken')

            if User.query.filter_by(email=email).first():
                form.email.errors.append(
                    'Account already exists for this address')
            return render_template('/user/signup.html', form=form)

        do_login(new_user)
        flash('Created your account!', 'success')

        return redirect('/trails/search')

    else:
        return render_template('/user/signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "info")
            return redirect('/trails/search')

        else:
            form.username.errors = ['Invalid username/password']

    return render_template('/user/login.html', form=form)


@app.route('/logout')
def logout_user():

    do_logout()
    flash("logged out", "warning")

    return redirect('/')


# TO BE IMPLEMENTED:
# @app.route('/forgotpassword', methods=['GET', 'POST'])
# def forgot_password():
#     """ Render forgot form. If email is valid and tied to an existing account, user will be sent an email """

#     form = Forgot()
#     if form.validate_on_submit():
#         email = form.email.data

#         try:
#             valid = validate_email(email, allow_smtputf8=False)

#         except:
#             return "Invalid Email Address"

#     else:
#         return render_template("/user/forgot.html", form=form, p_forg=True)


# @app.route('/forgotusername', methods=['GET', 'POST'])
# def forgot_username():
#     """ Render forgot form. If email is valid and tied to an existing account, user will be sent email """

#     form = Forgot()
#     if form.validate_on_submit():
#         email = form.email.data
#         try:
#             valid = validate_email(email, allow_smtputf8=False)

#             user = db.session.query(User).filter_by(email=email).first()

#             if not user:
#                 raise

#             mail = Mail(app)
#             msg = Message("Recover Username", sender="TrekAssure@gmail.com",
#                           recipients=[email])

#             msg.body = f"Your username is: {user.username}"
#             mail.send(msg)

#             flash("Sent Email!", "success")
#             return redirect('/')

#         except:
#             flash("Invalid Email", "warning")
#             return redirect('/')

#     else:
#         return render_template("/user/forgot.html", form=form, u_forg=True)


# *****************************
# M_KEY FOR FRONT END ROUTE
# *****************************

@app.route('/key')
def provide_key():
    if not g.user:
        flash("Please log in first", "danger")
        return redirect('/login')

    if 'unlocked' in session:
        del session['unlocked']
        return m_key

    else:
        flash("not authorized", "warning")
        return redirect('/')
