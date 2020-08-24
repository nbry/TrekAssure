import os
import requests
from flask import Flask, render_template, redirect
from flask_debugtoolbar import DebugToolbarExtension

from forms import TrailSearchForm, SecureHikeForm
from models import db, connect_db
from secrets import m_key, h_key
from functions import (search_for_trails, get_trail, get_conditions,
                       get_geo_info, rate_difficulty, get_directions, search_for_nearest,
                       secure_trip)


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


@app.route('/testing')
def show_testing_page():
    """ Temporary """
    return render_template('testing.html')


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

    if form.validate_on_submit():
        place_search = form.place_search.data
        radius = form.radius.data
        geo_info = get_geo_info(m_key, place_search)

        results = search_for_trails(h_key, geo_info['lat'],
                                    geo_info['lng'], radius)

        for trail in results:
            trail['difficulty'] = rate_difficulty(trail['difficulty'])

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
