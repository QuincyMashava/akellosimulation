from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, IntegerField, DateField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
import sqlalchemy as sa
from app import db
from app.models import User
from datetime import datetime
from wtforms.validators import NumberRange
from flask_wtf.file import FileField
from flask_ckeditor import CKEditorField


def validate_future_date(form, field):
    if field.data < datetime.today().date():
        raise ValidationError('Due date must be in the future.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField(('Department'), choices=[('Product Developement','Product Developement'), ('Sales & Marketing','Sales & Marketing'), ('Graphics','Graphics')], validators=[DataRequired()])
    role = SelectField(('Role'), choices=[('Software Engineer','Software Engineer'), ('Manager','Manager'), ('DevOps Engineer','DevOps Engineer') , ('Administrator','Administrator') ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


class AddNewSchoolTrackerForm(FlaskForm):
    schoolname = TextAreaField(('School Name'), validators=[DataRequired()])
    province = SelectField(('School Province'), choices=[('Harare','Harare'), ('Bulawayo','Bulawayo'), ('Manicaland','Manicaland'), ('Mashonaland Central','Mashonaland Central'), ('Mashonaland East','Mashonaland East'), ('Mashonaland West','Mashonaland West'), ('Masvingo','Masvingo'), ('Matabeleland North','Matabeleland North'), ('Matabeleland South','Matabeleland South'), ('Midlands','Midlands')], validators=[DataRequired()])
    district = TextAreaField(('School District'), validators=[DataRequired()])
    computers = IntegerField('Computers', validators=[NumberRange(min=0, max=100, message='Number of computers must be an integer')], default=0)
    internet = SelectField(('Internet Access ?'), choices=[('Yes','Yes'), ('No','No')], validators=[DataRequired()])
    lab = SelectField(('Access to Lab ?'), choices=[('Yes','Yes'), ('No','No')], validators=[DataRequired()])
    installed = SelectField(('Any Akello apps installed ?'), choices=[('None','None'), ('All','All'),('Akello Smartlearning','Akello Smartlearning'), ('Akello Library','Akello Library')], validators=[DataRequired()])
    scheduled_visit = SelectField(('Any scheduled visits ?'), choices=[('Yes','Yes'), ('No','No')], validators=[DataRequired()])
    tech_ready = SelectField(('Is the school tech ready ?'), choices=[('Yes','Yes'), ('No','No')], validators=[DataRequired()])
    installation_date = DateField('Installation Date', format='%Y-%m-%d', validators=[DataRequired(), validate_future_date])
    school_contact = TextAreaField(('School contact details'))
    submit = SubmitField('Add school to tracker')


class TaskForm(FlaskForm):
    description = CKEditorField(('Description'), validators=[DataRequired()])
    taskname = TextAreaField(('Task name'), validators=[DataRequired()])
    task_author =  TextAreaField(('Task author'))
    assigned_to = TextAreaField(('Assign task'))
    department = SelectField(('Department'), choices=[('None','None'),('Product Developement','Product Developement'), ('Sales & Marketing','Sales & Marketing'), ('Graphics','Graphics')])
    category = SelectField(('Category'), choices=[('Individual','Individual'), ('Department','Department')])
    status = SelectField(('Status'), choices=[('Pending','Pending'), ('Completed','Completed'),('Archived','Archived')])
    progress = IntegerField('Progress %', validators=[NumberRange(min=0, max=100, message='Progress must be between 0 and 100')], default=0)
    priority = SelectField(('Priority'), choices=[('Low','Low'),('Medium','Medium'),('Urgent','Urgent')], validators=[DataRequired()])
    # complete_date = DateField('Date Completed', format='%Y-%m-%d')
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired(), validate_future_date])
    submit = SubmitField('Submit')



class WorkspaceForm(FlaskForm):
    name = StringField('Workspace Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    members = SelectMultipleField('Members', coerce=int)  # coerce=int to store user IDs
    submit = SubmitField('Create Workspace')

