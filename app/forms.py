from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectMultipleField, TextAreaField, widgets
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length

from app.models import User, Role, Group, Task

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('User does not exist')

    # def validate_password(self, password):
    #     user = User.query.filter_by(username=self.username.data).first()
    #     if not user.check_password(password.data) and user:
    #         raise ValidationError('Password incorrect')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = RadioField('Status', choices=[
                            (role.rolename, role.rolename) for role in Role.query.all()
                            ],
                            validators=[DataRequired()])
    submit = SubmitField('Register', validators=[DataRequired()])


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140, message="Don't joke with me")])
    # age = StringField('Age', validators=[Length(min=0, max=3)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class CreateGroup(FlaskForm):
    groupname = StringField('Groupname', validators=[DataRequired(), Length(min=0, max=20)])
    description = TextAreaField('Info', validators=[DataRequired(), Length(min=0, max=140,  message="Description must be less then 140 symbols!")])
    submit = SubmitField('Create group', validators=[DataRequired()])

    def validate_groupname(self, groupname):
        group = Group.query.filter_by(groupname=groupname.data).first()
        if group is not None:
            raise ValidationError('Please use a different groupname.')


class EditGroupForm(FlaskForm):
    groupname = StringField('Groupname', validators=[DataRequired(), Length(min=0, max=20)])
    description = TextAreaField('Info', validators=[Length(min=0, max=140, message="Description must be less then 140 symbols!")])
    submit = SubmitField('Submit')

    def __init__(self, original_groupname, *args, **kwargs):
        super(EditGroupForm, self).__init__(*args, **kwargs)
        self.original_groupname = original_groupname


    def validate_groupname(self, groupname):
        if groupname.data != self.original_groupname:
            group = Group.query.filter_by(groupname=self.groupname.data).first()
            if group is not None:
                raise ValidationError('Please use a different groupname.')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class TaskForm(FlaskForm):
    task = StringField('Task name', validators=[DataRequired(), Length(min=0, max=35)])
    body = TextAreaField('Task description', validators=[Length(min=0, max=140)])
    price = StringField('Task price', validators=[DataRequired(), Length(min=0, max=5)])
    groups = MultiCheckboxField('Choose group', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit')


    def validate_price(self, price):
        try:
            price = int(price.data)
        except:
            raise ValidationError('Please type integer number')


class EditTaskForm(FlaskForm):
    taskname = StringField('Task name', validators=[DataRequired(), Length(min=0, max=35)])
    body = TextAreaField('Task description', validators=[Length(min=0, max=140)])
    price = StringField('Task price', validators=[DataRequired(), Length(min=0, max=5)])
    groups = MultiCheckboxField('Choose group', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_price(self, price):
        try:
            price = int(price.data)
        except:
            raise ValidationError('Please type integer number')

