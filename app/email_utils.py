import secrets
import string
from flask import current_app, render_template
from flask_mail import Message
from app import mail

def generate_random_password(length=12):
    """Generate a random password with letters, digits, and symbols"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_welcome_email(user):
    """Send welcome email to newly registered user"""
    try:
        msg = Message(
            subject="Welcome to DataCharted! 🎉",
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML version
        msg.html = render_template('emails/welcome.html', user=user)
        
        # Plain text version
        msg.body = render_template('emails/welcome.txt', user=user)
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False

def send_password_reset_email(user, new_password):
    """Send password reset email with new password"""
    try:
        msg = Message(
            subject="Your DataCharted Password Has Been Reset",
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML version
        msg.html = render_template('emails/password_reset.html', user=user, new_password=new_password)
        
        # Plain text version
        msg.body = render_template('emails/password_reset.txt', user=user, new_password=new_password)
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False
