from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, BooleanField, HiddenField
from wtforms.validators import InputRequired, Length, Email


class TrailSearchForm(FlaskForm):
    """ Form for searching for trails """
    search_radius_choices = [10, 20, 30, 40, 50, 100]

    place_search = StringField('Search Place', validators=[InputRequired()])
    radius = SelectField('Search Radius', validators=[
                         InputRequired()], choices=[(c, str(c) + ' miles') for c in search_radius_choices])


class SecureHikeForm(FlaskForm):
    """ Requests user address and preferences for hiking pamphlet """

    home_address = StringField(
        'Home Address', validators=[InputRequired()])


class UserSignupForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(
        min=5, max=15, message="Username must be 5-15 characters long")])
    password = PasswordField("Password", validators=[
                             InputRequired(), Length(min=5, message="Password must be 5 characters or longer")])
    email = StringField("Email", validators=[
                        Email("Please enter a valid email address")])
    address = StringField("Home Address (optional)")

    new_password = PasswordField("New Password")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class Forgot(FlaskForm):
    email = StringField("Email", validators=[
                        Email("Please enter a valid email address")])
