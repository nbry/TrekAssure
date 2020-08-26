import os
import requests
from flask import Flask, render_template, redirect, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import TrailSearchForm, SecureHikeForm, UserSignupForm, LoginForm
from models import db, connect_db, User
from secrets import m_key, h_key
from functions import (search_for_trails, get_trail, get_conditions,
                       get_geo_info, rate_difficulty, get_directions, search_for_nearest,
                       secure_trip)

CURR_USER_KEY = "curr_user"

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
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def store_search(results, radius, geo_info):
    """ Store trail search results in g in case user refreshes """

    if CURR_USER_KEY in session:
        g.user_search = {
            'results': results,
            'radius': radius,
            'geo_info': geo_info
        }


@app.route('/')
def home_page():
    """ Show Home Page """
    return render_template("extends.html")

# *****************************
# "TRAIL"  ROUTES
# *****************************


@app.route('/trails/search', methods=['GET', 'POST'])
def search_trail_form():
    """ Render page that shows a form that allows
    a user to serach for a trail """
    form = TrailSearchForm()

    # If user is logged in and refreshes after searching, show same results
    # if CURR_USER_KEY in session:

    if form.validate_on_submit():
        place_search = form.place_search.data
        radius = form.radius.data
        geo_info = get_geo_info(m_key, place_search)
        results = search_for_trails(h_key, geo_info['lat'],
                                    geo_info['lng'], radius)

        for trail in results:
            trail['difficulty'] = rate_difficulty(trail['difficulty'])

        store_search(results, radius, geo_info)
        return render_template("/trail/search_results.html",
                               results=results,
                               radius=radius,
                               city=geo_info['city'])
    else:
        return render_template("/trail/search_form.html", form=form)


@app.route('/trails/<int:trail_id>/secure', methods=['GET', 'POST'])
def secure_hike(trail_id):
    """ Render page that shows a form to sign in, or continue as guest.
    As a guest, user can input starting address and preferences to request info.
    Signed in Users will get results based on their preferences """

    form = SecureHikeForm()
    # WORK IN PROGRESS BELOW:
    # if session['CURR_USER']:
    #     return redirect('/')

    if form.validate_on_submit():
        home_address = form.home_address.data
        trail = get_trail(h_key, trail_id)

        secured_trip = secure_trip(m_key, trail, home_address)

        return render_template('/trail/secure_results.html', secured_trip=secured_trip, trail=trail)

    else:
        return render_template('/trail/secure_form.html', form=form, trail_id=trail_id)


# *****************************
# "USER"  ROUTES
# *****************************

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
        flash('Successfully created your account!', 'success')

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
