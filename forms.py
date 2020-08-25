from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, Email

choices = [5, 10, 15, 20, 25, 50, 100]


class TrailSearchForm(FlaskForm):
    """ Form for searching for trails """

    place_search = StringField('Search Place', validators=[InputRequired()])
    radius = SelectField('Within', validators=[
                         InputRequired()], choices=[(c, str(c) + ' miles') for c in choices])


class SecureHikeForm(FlaskForm):
    """ Requests user address and preferences for hiking pamphlet """

    home_address = StringField(
        'Home Address', validators=[InputRequired()])
    # hospital = BooleanField('hospital')
    # gas_station = BooleanField('gas station')
    # pharmacy = BooleanField('pharmacy')
    # police_station = BooleanField('police station')


class UserSignupForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(
        min=6, max=15, message="Username must be 6-15 characters long")])
    password = PasswordField("Password", validators=[
                             InputRequired(), Length(min=6)])
    email = StringField("Email (optional)", validators=[
                        Email("Please enter a valid email address")])
    address = StringField("Home Address (optional)")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
