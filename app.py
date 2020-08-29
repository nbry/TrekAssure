import os
import requests
from flask import Flask, render_template, redirect, session, flash, g, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import TrailSearchForm, UserSignupForm, LoginForm, SecureHikeForm
from models import db, connect_db, User, TrailsSearch, SecuredHikePamphlet
from secrets import m_key, h_key
from functions import (search_for_trails, get_trail, get_conditions,
                       get_geo_info, rate_difficulty, get_directions, search_for_nearest,
                       secure_trip)

CURR_USER_KEY = "curr_user"
SEARCH_ID = "SEARCH_ID"
FILTERED_RESULTS = "FILTERED_RESULTS"


app = Flask(__name__)
MQAPI_BASE_URL = 'http://www.mapquestapi.com/'
HPAPI_BASE_URL = 'https://www.hikingproject.com/data'

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
def add_user_to_g():
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


@app.route('/')
def home_page():
    """ Show Home Page """
    return render_template("extends.html")

# *****************************
# TREKASSURE "TRAIL SEARCH" DATA REQUEST HANDLING
# *****************************


@app.route('/trails/results')
def get_trails():
    """ Handle a request (from front end) and respond with
    a JSON object with trail info """

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

@app.route('/trails/refresh')
def refresh_trails():
    """ User cliked 'Find Your Trail' Button. Clear previous search results """

    if SEARCH_ID in session:
        del session[SEARCH_ID]

    return redirect('/trails/search')


@app.route('/trails/search')
def show_search_results():
    """ Render a form that shows "Find Your Trail" form """

    form_t = TrailSearchForm()
    form_s = SecureHikeForm()
    if SEARCH_ID in session:
        return render_template("/trail/search_form.html", form_t=form_t, form_s=form_s, results=g.search.data)

    else:
        return render_template("/trail/search_form.html", form_t=form_t, form_s=form_s, results=None)


@app.route('/trails/<int:trail_id>')
def show_trail(trail_id):
    """ Render a page that shows detail about a trail, should the user manually search by id.
    Also serves as the default route if user tampers with user/{id}/pamphlets URL.
    This route is not an explicit feature of TrekAssure. It's more of a quality of life consideration """

    try:
        trail = get_trail(h_key, trail_id)
        trail['difficulty'] = rate_difficulty(trail['difficulty'])

        return render_template('/trail/trail_info.html', result=trail)

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

        flash("Secured your hike!", "success")
        return redirect(f'/users/{g.user.id}/pamphlets/{pamphlet_to_db.id}')

    else:
        form_t = TrailSearchForm()
        return render_template('/trail/search_form.html', form_t=form_t, form_s=form_s, trail_id=trail_id)


# *****************************
# USER PAMPHLET ROUTE
# *****************************

@app.route('/users/<int:user_id>/pamphlets/<int:pamphlet_id>')
def show_secured_hike_pamphlet(user_id, pamphlet_id):
    """ Route that shows saved user pamphlets. If session user does not match user_id, 
    then redirect back to trail route. """

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect("/trails/search")

    pamphlet = SecuredHikePamphlet.query.get_or_404(pamphlet_id)
    secured_trip = pamphlet.data
    trail = get_trail(h_key, pamphlet.trail_id)

    return render_template('/trail/secure_results.html', secured_trip=secured_trip, trail=trail)

# *****************************
# USER ACCOUNT ROUTES
# *****************************


@app.route('/users/<int:user_id>')
def show_user_profile(user_id):
    """ Show user profile. If session user does not match user_id, redirect to trail route """

    if user_id != g.user.id:
        flash("Not authorized to view that page", "warning")
        return redirect("/trails/search")

    user_info = User.query.get(g.user.id)

    return render_template('/user/profile.html', user=user_info)


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
