from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField
from wtforms.validators import InputRequired

choices = [5, 10, 15, 20, 25, 50, 100]


class TrailSearchForm(FlaskForm):
    """ Form for searching for trails """

    zip_code = IntegerField('Zip Code', validators=[InputRequired()])
    radius = SelectField('Search Within', validators=[
                         InputRequired()], choices=[(c, str(c) + ' miles') for c in choices])
