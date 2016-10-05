from datetime import datetime
from main import db


class User(db.Model):
    """User model description"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    public_key = db.Column(db.Text)

    def __init__(self, username, pub_key):
        self.username = username
        self.public_key = pub_key

    def __str__(self):
        return "<Username: %s>" % (self.username)


class Messages(db.Model):
    """Message model description"""
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(255))
    recipient = db.Column(db.Integer, db.ForeignKey('user.id'))
    message_id = db.Column(db.Integer)
    encrypted_message = db.Column(db.Text)
    date = db.Column(db.TIMESTAMP)

    def __init__(self, sender, recipient, msg_id, enc_message, date=None):
        self.sender = sender
        self.recipient = recipient
        self.message_id = msg_id
        self.encrypted_message = enc_message
        if date is None:
            self.date = datetime.utcnow()
        else:
            self.date = date
