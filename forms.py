from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, EmailField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a new cafe
class CafeForm(FlaskForm):
    cafe_name = StringField('Cafe name', validators=[DataRequired()])
    location = StringField('Cafe Location on Google Maps (URL)', validators=[DataRequired(), URL()])
    open = StringField('Opening Time e.g. 8AM', validators=[DataRequired()])
    close = StringField('Closing Time e.g. 5:30PM', validators=[DataRequired()])
    coffee_rating = SelectField('Coffee Rating', choices=['☕','☕☕','☕☕☕','☕☕☕☕','☕☕☕☕☕'], validators=[DataRequired()])
    wifi_rating = SelectField('Wifi Strenght Rating', choices=['✘', '💪','💪💪','💪💪💪','💪💪💪💪','💪💪💪💪💪'], validators=[DataRequired()])
    power_rating = SelectField('Power Socket Availability', choices=['✘','🔌','🔌🔌','🔌🔌🔌','🔌🔌🔌🔌','🔌🔌🔌🔌🔌'], validators=[DataRequired()])
    img_url = StringField('Cafe Image URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')
    cancel = SubmitField(label='Cancel')


# RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    name = StringField(label='Name', validators=[DataRequired()])
    submit = SubmitField(label='Sign me up!')
    cancel = SubmitField(label='Cancel')
    

# LoginForm to login existing users
class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Log In')
    cancel = SubmitField(label='Cancel')

# CommentForm so users can leave comments below a cafe
class CommentForm(FlaskForm):
    body = CKEditorField("Comment Content", validators=[DataRequired()])
    submit = SubmitField('Submit')
    cancel = SubmitField(label='Cancel')
