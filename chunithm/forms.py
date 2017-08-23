from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import validators
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('Password', validators=[InputRequired(), validators.Length(min=6, max=200)])