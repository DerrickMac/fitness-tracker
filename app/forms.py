from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateTimeField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, length, Optional
import sqlalchemy as sa
from app import db
from app.models import User
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data
        ))
        if user is not None:
            raise ValidationError('Username already exists. Please use a different username')
        
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data
        ))
        if user is not None:
            raise ValidationError('Email already registered. Please instead login or register a different email address')
    
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        # Case where user tries to change username to an existing username in the DB.
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data
            ))
            # if DB finds a match to the submitted username change, throw error
            if user is not None:
                raise ValidationError('Please use a different username')

class WorkoutForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    exercise_type = SelectField('Exercise Type', choices=[('machine', 'Machine'), ('free_weight', 'Freeweight'), ('bodyweight', 'Bodyweight'), ('cardio', 'Cardio')], validators=[DataRequired()])
    muscle_group = SelectField('Muscle Group', choices=[('abs', 'Abs'), ('back', 'Back'), ('biceps', 'Biceps'), ('calves', 'Calves'), ('chest', 'Chest'), ('chest_lower', 'Chest (Lower)'), ('chest_upper', 'Chest (Upper)'), ('forearms', 'Forearms'), ('glutes', 'Glutes'), ('hamstrings', 'Hamstrings'),  ('heart', 'Heart'), ('hip_flexors', 'Hip Flexors'), ('inner_thighs', 'Inner thighs'), ('lats', 'Lats'), ('lower_back', 'Lower Back'), ('quadriceps', 'Quadriceps'), ('shoulders', 'Shoulders'), ('triceps', 'Triceps'),], validators=[DataRequired()])
    submit = SubmitField('Submit')

class ExerciseForm(FlaskForm):
    date = DateTimeField('Date', format='%Y-%m-%d', default=datetime.now(), validators=[DataRequired()])
    weight = IntegerField('Weight (lbs)', validators=[Optional()])
    count = IntegerField('Count', validators=[Optional()])
    distance = IntegerField('Distance (miles)', validators=[Optional()])
    submit = SubmitField('Submit')