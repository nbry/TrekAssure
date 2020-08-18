import os
from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from forms import TrailSearchForm
from models import db, connect_db


app = Flask(__name__)


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


@app.route('/trails/search')
def search_trail_form():
    """ Render page that shows a form that allows
    a user to serach for a trail """
    form = TrailSearchForm()

    choices = [5, 10, 15, 20, 25, 50, 100]
    form.radius.choices = [(c, c) for c in choices]

    return render_template("/trail/search_form.html", form=form)
