from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import InputRequired


class TrailSearchForm(FlaskForm):
    """ Form for searching for trails """

    city = StringField('City', validators=[InputRequired()])
    radius = SelectField('Search Within', validators=[InputRequired()])
