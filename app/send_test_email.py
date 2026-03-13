from flask import Flask
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

def send_test_email():
    with app.app_context():
        msg = Message(
            subject="Test Email Flask",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=["sautajoseph11@gmail.com"],
            body="Ceci est un email de test envoyé depuis Flask-Mail, nous sommes en train de configurer l'application, merci."
        )
        mail.send(msg)
        print("Email envoyé avec succès.")

if __name__ == "__main__":
    send_test_email()
