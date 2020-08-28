from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, BooleanField, HiddenField
from wtforms.validators import InputRequired, Length, Email

choices = [10, 20, 30, 40, 50, 100]


class TrailSearchForm(FlaskForm):
    """ Form for searching for trails """

    place_search = StringField('Search Place', validators=[InputRequired()])
    radius = SelectField('Search Radius', validators=[
                         InputRequired()], choices=[(c, str(c) + ' miles') for c in choices])


class SecureHikeForm(FlaskForm):
    """ Requests user address and preferences for hiking pamphlet """

    home_address = StringField(
        'Home Address', validators=[InputRequired()])


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
