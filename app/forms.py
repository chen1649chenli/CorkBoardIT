from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms import SelectField
import app


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    pin = PasswordField('Pin', validators=[DataRequired()])
    submit = SubmitField('Login')


class AddPushpinForm(FlaskForm):
    url = StringField('Url', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[
        DataRequired(), Length(min=1, max=200, message="Description must be shorter than 200 characters")])
    tags = StringField('Tags', validators=[DataRequired()])
    submit = SubmitField('Add')

    def validate_url(self, url):
        extension = url.data.split(".", 1)[-1].lower()
    
        correct_extension = "jpg" in extension or "png" in extension or "gif" in extension
        if not correct_extension:
            raise ValidationError('Must be a jpg, png or gif')


class AddCorkBoardForm(FlaskForm):
    title = StringField('Url', validators=[DataRequired()])
    dropdown_list = ['Air', 'Land', 'Sea'] # You can get this from your model
    category = SelectField('Delivery Types', choices=dropdown_list, default=1)
    boardPassword = StringField('password')
    submit = SubmitField('Add')


class LikePushpinForm(FlaskForm):
    submit = SubmitField('like')


class UnlikePushpinForm(FlaskForm):
    submit = SubmitField('unlike')


class CommentForm(FlaskForm):
    submit = SubmitField('comment')