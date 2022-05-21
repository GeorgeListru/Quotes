from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import ast
from flask_mail import Message, Mail

sender_email = ""
password = ""
app = Flask(__name__)
CORS(app)
app.config.update({
    "DEBUG": False,
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": sender_email,
    "MAIL_PASSWORD": password
})
mail = Mail(app)
mail.init_app(app)


@app.route("/send-email", methods=['POST'])
def send_email():
    data = ast.literal_eval(list(request.form)[0])
    receiver_email = data.get('email')
    subject = "+" + str(len(data.get('quotes'))) + " new quotes for you!"

    msg = Message(subject=subject, sender=sender_email, recipients=[receiver_email, ])
    msg.html = render_template('EmailTemplate.html', quotes=data.get('quotes'))
    mail.send(msg)
    message = {'detail': "Email sent successfully"}
    return jsonify(message)
