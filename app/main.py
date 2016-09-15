# Server part of the JMessage messaging client, used for Practical Cryptographic
# Systems at JHU.

# Author: J. Ayo Akinyele <jakinye3@jhu.edu>

from flask import Flask, request, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = "W9zmH5FLJuDHNia3xW4yyg=="
db = SQLAlchemy(app)
debug = False
# this deletes messages in users inbox after delivery
delete_after_delivery = True

#TODO: add signup/authentication for users
#TODO: add session management

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
    sender = db.Column(db.String(255), db.ForeignKey('user.id'))
    recipient = db.Column(db.String(255))
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


@app.route('/lookupUsers', methods=['GET'])
def api_lookup_users():
    """get all the users in the system"""
    users = User.query.all()
    data = {'users': [], 'numUsers': 0}
    if users:
        data['users'] = [u.username for u in users]
        data['numUsers'] = len(data['users'])
    return Response(json.dumps(data), status=200, mimetype='application/json')


@app.route('/lookupKey/<userid>', methods=['GET'])
def api_lookup_key(userid):
    """lookup a specific user's public key"""
    user = User.query.filter_by(username=userid).first()
    if user:
        data = {'keyData': user.public_key}
    else:
        data = {'keyData': ""}
    return Response(json.dumps(data), status=200, mimetype='application/json')


@app.route('/registerKey/<userid>', methods=['POST'])
def api_register_key(userid):
    """register a new public key for a user"""
    resp_data = {'result': True}
    if request.headers['Content-Type'] == 'application/json':
        keyData = request.json.get('keyData')
        if keyData is None:
            # 401 => bad request
            resp_data['result'] = False
            return Response(json.dumps(resp_data), status=401, mimetype='application/json')
        if debug:
            print("KeyData: ", keyData)
            print("UserID: ", userid)

        user = User.query.filter_by(username=userid).first()
        if user is None:
            # NOTE: we do not validate public keys. This is just dumb storage.
            user = User(username=userid, pub_key=keyData)
        else:
            user.public_key = keyData
        db.session.add(user)
        db.session.commit()
        # 200 => OK
        return Response(json.dumps(resp_data), status=200, mimetype='application/json')
    else:
        return "415 Unsupported Media Type"


@app.route('/getMessages/<userid>', methods=['GET'])
def api_get_messages(userid):
    """get the messages for a given user"""
    message_contents = Messages.query.filter_by(recipient=userid)
    messages = []
    for m in message_contents:
        timestamp = int((m.date - datetime(1970,1,1)).total_seconds())
        messages.append({'senderID': m.sender,
                          'messageID': m.message_id,
                          'message': m.encrypted_message,
                          'sentTime': timestamp})
        if delete_after_delivery:
            db.session.delete(m)
            db.session.commit()

    data = {'messages': messages, 'numMessages': len(messages)}
    js = json.dumps(data)
    return Response(js, status=200, mimetype='application/json')


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

@app.route('/sendMessage/<userid>', methods=['POST'])
def api_send_message(userid):
    """send message from one user to another"""
    resp_data = {'result': False, 'message': None}
    if request.headers['Content-Type'] == 'application/json':
        message = request.json
        recipient = message.get('recipient')
        if recipient is None:
            resp_data['message'] = 'missing the recipient'
            return Response(json.dumps(resp_data), status=401, mimetype='application/json')
        enc_message = message.get('message')
        if enc_message is None:
            resp_data['message'] = 'missing the encrypted message'
            return Response(json.dumps(resp_data), status=401, mimetype='application/json')
        message_id = message.get('messageID')
        if message_id is None or not isInt(message_id):
            resp_data['message'] = 'missing message ID'
            return Response(json.dumps(resp_data), status=401, mimetype='application/json')

        m = Messages(userid, recipient, message_id, enc_message)
        db.session.add(m)
        db.session.commit()
        resp_data['result'] = True
        resp_data['message'] = 'message delivered'
        return Response(json.dumps(resp_data), status=200, mimetype='application/json')
    else:
        return "415 Unsupported Media Type"


@app.route("/")
def main():
    return send_file('./static/index.html')

PORT = 80
DEBUG_PORT = 8080
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=PORT)
