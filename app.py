import os
import requests
from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from forms import TrailSearchForm
from models import db, connect_db
from secrets import m_key, h_key
from functions import search_for_trails, get_trail, get_conditions, get_geo_info


app = Flask(__name__)
MQAPI_BASE_URL = 'http://www.mapquestapi.com/geocoding/v1/'
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


@app.route('/')
def home_page():
    """ Show Home Page """
    return render_template("extends.html")


@app.route('/trails/search', methods=['GET', 'POST'])
def search_trail_form():
    """ Render page that shows a form that allows
    a user to serach for a trail """
    form = TrailSearchForm()

    if form.validate_on_submit():
        zip_code = form.zip_code.data
        radius = form.radius.data
        geo_info = get_geo_info(zip_code)

        results = search_for_trails(
            h_key,
            geo_info['lat'],
            geo_info['lng'],
            radius
        )

        return render_template("/trail/search_results.html",
                               results=results,
                               radius=radius,
                               city=geo_info['major_city'])

    return render_template("/trail/search_form.html", form=form)
