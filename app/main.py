# Server part of the JMessage messaging client, used for Practical Cryptographic
# Systems at JHU.

# Author: J. Ayo Akinyele <jakinye3@jhu.edu>

from flask import Flask, request, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

debug = True
# this deletes messages in users inbox after delivery
delete_after_delivery = True

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = str(os.environ.get('DATABASE_URI', 'sqlite:////data/messages.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = "W9zmH5FLJuDHNia3xW4yyg=="
db = SQLAlchemy(app)
# import appropriate models
from models import User, Messages

try:
    db.create_all()
    db.session.commit()
    if debug: print("DB tables created successfully...")
except:
    pass

#TODO: add signup/authentication for users
#TODO: add session management

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
        data = {'keyData': user.public_key, 'status': "found key"}
    else:
        data = {'keyData': "", 'status': "no registered key"}
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
    r = User.query.filter_by(username=userid).first()
    if r is None:
        data = {'messages': [], 'numMessages': 0}
        return Response(json.dumps(data), status=200, mimetype='application/json')

    message_contents = Messages.query.filter_by(recipient=r.id)
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

        r = User.query.filter_by(username=recipient).first()
        if r is None:
            resp_data['message'] = 'no such recipient'
            return Response(json.dumps(resp_data), status=401, mimetype='application/json')

        m = Messages(userid, r.id, message_id, enc_message)
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
