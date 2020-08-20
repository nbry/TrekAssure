from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, BooleanField
from wtforms.validators import InputRequired

choices = [5, 10, 15, 20, 25, 50, 100]


class TrailSearchForm(FlaskForm):
    """ Form for searching for trails """

    zip_code = IntegerField('Zip Code', validators=[InputRequired()])
    radius = SelectField('Search Within', validators=[
                         InputRequired()], choices=[(c, str(c) + ' miles') for c in choices])


class SecureHikeForm(FlaskForm):
    """ Requests user address and preferences for hiking pamphlet """

    starting_address = StringField(
        'Starting Address', validators=[InputRequired()])
    # hospital = BooleanField('hospital')
    # gas_station = BooleanField('gas station')
    # pharmacy = BooleanField('pharmacy')
    # police_station = BooleanField('police station')
