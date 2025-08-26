from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User
import re

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(max=64, message='First name must be less than 64 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(max=64, message='Last name must be less than 64 characters')
    ])
    company_name = StringField('Company Name', validators=[
        Length(max=128, message='Company name must be less than 128 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        # Check if email already exists
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another email or login.')
    
    def validate_password(self, password):
        # Check password strength
        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        # Check for at least one uppercase letter, one lowercase letter, and one number
        if not re.search(r'[A-Z]', password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', password.data):
            raise ValidationError('Password must contain at least one number.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
    
    def validate_password(self, password):
        # Check password strength
        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        # Check for at least one uppercase letter, one lowercase letter, and one number
        if not re.search(r'[A-Z]', password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', password.data):
            raise ValidationError('Password must contain at least one number.')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(max=64, message='First name must be less than 64 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(max=64, message='Last name must be less than 64 characters')
    ])
    company_name = StringField('Company Name', validators=[
        Length(max=128, message='Company name must be less than 128 characters')
    ])
    submit = SubmitField('Update Profile')
