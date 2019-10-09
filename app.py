import time
import json
from flask import Flask, request, Response, jsonify
from flask_mongoengine import *
from functools import wraps
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, decode_token)
import datetime
# testing mongoengine
from models.User import User
from models.DiaryEntry import DiaryEntry
# for getting environment variables
import os

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {
    'db': os.environ['DB_NAME'], 'host': os.environ['DB_URI']}

app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']

mongo = MongoEngine(app)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Checks username and password


def check_auth(username, password):
    return username == 'diary' and password == 'diaryapp'
# Returns if authenticated or not


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})
# creates the decorator the enables auth on endpoints


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/getAllEntries', methods=['POST'])
def getAllEntries():
    entries = []
    Payload = request.json
    for x in DiaryEntry.objects(userID=Payload["userID"]).order_by("-entryDate").limit(7).skip(Payload["skip"]):
        print(x)
        entries.append(
            {
                "_id": str(x["id"]),
                "title": x["title"],
                "body": x["body"],
                "entryDate": x["entryDate"],
                "updateTS": x["updateTS"],
                "userID": x["userID"]
            }
        )
    return jsonify({"Success": True,
                    "Data": entries
                    })


@app.route('/insertEntry', methods=['POST'])
@requires_auth
def insertEntry():
    # change request received through endpoint to JSON
    Payload = request.json
    newEntry = DiaryEntry(
        title=Payload["title"],
        body=Payload["body"],
        entryDate=Payload["entryDate"],
        updateTS=datetime.datetime.now().isoformat(),
        userID=Payload["userID"]
    )
    newEntry.save()
    return jsonify({"Success": True})


@app.route('/editEntry', methods=['PUT'])
@requires_auth
def deleteEntry():
    # change request received through endpoint to JSON
    Payload = request.json
    current_Datetime = datetime.datetime.now().isoformat()
    # Gets string from ObjectID
    user_exists = DiaryEntry.objects(id=Payload["_id"]).first().update(
        set__title=Payload["title"],
        set__entryDate=Payload["entryDate"],
        set__body=Payload["body"],
        set__updateTS=current_Datetime
    )
    return jsonify({"Success": True})


@app.route('/deleteEntry', methods=['POST'])
@requires_auth
def editEntry():
    # change request received through endpoint to JSON
    Payload = request.json
    DiaryEntry.objects(id=Payload["_id"]).first().delete()
    return jsonify({"Success": True})


@app.route('/users/registerUser', methods=['POST'])
@requires_auth
def createUser():
    # change request received through endpoint to JSON
    Payload = request.json
    # Check if user is in DB
    user_exists = ""
    user_exists = User.objects(username=Payload["username"])
    if user_exists:
        # Error if user exists
        return jsonify({
            "Success": False,
            "Message": "User Already Exists"
        }), 201
    else:
        # If user does not exist
        Payload["password"] = bcrypt.generate_password_hash(
            Payload["password"]).decode('utf-8')
        new_user = User(
            username=Payload["username"], password=Payload["password"])
        new_user.save()
        access_token = create_access_token(identity={
            "username": Payload["username"],
            "id": str(new_user["id"])
        }, expires_delta=None)
        return jsonify({"Success": True, "Token": access_token})


@app.route('/users/login', methods=['POST'])
@requires_auth
def login():
    # change request received through endpoint to JSON
    Payload = request.json
    user_exists = ""
    user_exists = User.objects(username=Payload["username"]).first()
    if user_exists:
        if bcrypt.check_password_hash(user_exists.password, Payload["password"]):
            # if username exists - and password is correct - create JWT Token
            access_token = create_access_token(identity={
                "username": user_exists.username,
                "id": str(user_exists.id)
            }, expires_delta=None)
            return jsonify({"Success": True, "Token": access_token})
        else:
            # If username exists - and password is incorrect - return error
            return jsonify(
                {
                    "Success": False, 
                    "Message": "Wrong username/password combination"
                }
            ), 401
    else:
            # If user does not exist - return error
        return jsonify(
            {
                "Success": False, 
                "Message": "username does not exist, please register"
            }
        ), 401


@app.route('/users/loginGoogleUser', methods=['POST'])
@requires_auth
def loginGoogleUser():
    # change request received through endpoint to JSON
    Payload = request.json
    # Check if user is in DB
    user_exists = ""
    user_exists = User.objects(username=Payload["username"])
    if user_exists:
        access_token = create_access_token(identity={
            "username": user_exists.username,
            "id": str(user_exists.id)
        }, expires_delta=None)
        # if user exists
        return jsonify({
            "Success": True,
            "Token": access_token
        }), 200
    else:
        # If user does not exist - create in DB
        new_user = User(
            username=Payload["username"],
            
            )
        new_user.save()
        access_token = create_access_token(identity={
                "username": new_user.username,
                "id": str(new_user.id)
            }, expires_delta=None)
        return jsonify(
            {
                "Success": True,
                "Token" : access_token
            }
        )

def token_decode(access_token):
    decoded_token = decode_token(access_token)
    user_id = decoded_token["identity"]["id"]
    return user_id


if __name__ == "__main__":
    # Running the flask app
    # This previous setting enables SSL - commented out in the current file
    #app.run(host="0.0.0.0", ssl_context='adhoc')
    app.run()
