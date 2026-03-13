from flask import current_app
from flask_mail import Message
from app.extensions import mail

def send_email(subject, recipients, body, html=None):
    msg = Message(
        subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=recipients
    )
    msg.body = body
    if html:
        msg.html = html
    mail.send(msg)
