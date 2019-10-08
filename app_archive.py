import time
import json
from flask import Flask, request, Response, jsonify
from flask_pymongo import PyMongo
from functools import wraps
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, decode_token)
import datetime
# testing mongoengine
from models.User import User

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://root:password1@ds151086.mlab.com:51086/diary_app"
app.config["JWT_SECRET_KEY"] = 'secret'

mongo = PyMongo(app)
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
    for x in mongo.db.diary_entries.find().sort("entryDate", -1).limit(7).skip(Payload["skip"]):
        print(x)
        entries.append(
            {
                "_id": str(x["_id"]),
                "title": x["title"],
                "body": x["body"],
                "entryDate": x["entryDate"],
                "updateTS": x["updateTS"]
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
    Payload["updateTS"] = datetime.datetime.now().isoformat()
    diaryEntry = mongo.db.diary_entries.insert_one(Payload)
    return jsonify({"Success": True})


@app.route('/editEntry', methods=['PUT'])
@requires_auth
def deleteEntry():
    # change request received through endpoint to JSON
    Payload = request.json
    current_Datetime = datetime.datetime.now().isoformat()
    # Gets string from ObjectID
    diaryEntry = mongo.db.diary_entries.update_one(
        {
            "_id": ObjectId(Payload["_id"])
        },
        {
            "$set": {
                "title": Payload["title"],
                "entryDate": Payload["entryDate"],
                "body": Payload["body"],
                "updateTS": current_Datetime
            }
        }
    )
    return jsonify({"Success": True})


@app.route('/deleteEntry', methods=['POST'])
@requires_auth
def editEntry():
    # change request received through endpoint to JSON
    Payload = request.json
    # Gets string from ObjectID
    diaryEntry = mongo.db.diary_entries.delete_one(
        {
            "_id": ObjectId(Payload["_id"])
        })
    return jsonify({"Success": True})



@app.route('/users/registerUser', methods=['POST'])
@requires_auth
def createUser():
    # change request received through endpoint to JSON
    Payload = request.json
    #Check if user is in DB
    user_exists = ""
    user_exists = mongo.db.User.find_one({'Email' : Payload["Email"]})
    if user_exists:
        #Error if user exists
        return jsonify({
            "Success" : False, 
            "Message" : "User Already Exists"
        }), 201
    else:
        #If user does not exist
        Payload["Password"] = bcrypt.generate_password_hash(Payload["Password"]).decode('utf-8')
        new_user = User(Email = Payload["Email"], Password = Payload["Password"])
        #create new user object and insert it into mongodb
        new_user = json.dumps(new_user.__dict__)
        new_user = json.loads(new_user)
        diaryEntry = mongo.db.User.insert_one(new_user)
        return jsonify({"Success": True})


@app.route('/users/login', methods=['POST'])
@requires_auth
def login():
    # change request received through endpoint to JSON
    Payload = request.json
    user_exists = ""
    user_exists = mongo.db.User.find_one({'Email' : Payload["Email"]})
    if user_exists:
        if bcrypt.check_password_hash(user_exists["Password"], Payload["Password"]):
            #if username exists - and password is correct - create JWT Token
            access_token = create_access_token(identity = {
                "Email" : user_exists["Email"],
                "id" : str(user_exists["_id"])
            }, expires_delta = None)
            token_decode(access_token)
            return jsonify({"Success": True, "Token" : access_token})
        else:
            #If username exists - and password is incorrect - return error
            return jsonify({"Success" : False , "Message" : "Wrong email/password combination"}), 401
    else:
            #If user does not exist - return error
        return jsonify({"Success" : False, "Message" : "Email does not exist, please register"})



def token_decode(access_token):
    decoded_token = decode_token(access_token)
    user_id = decoded_token["identity"]["id"]
    return user_id


@app.route('/users/registertestUser', methods=['POST'])
@requires_auth
def createtestUser():
    # change request received through endpoint to JSON
    Payload = request.json
    #Check if user is in DB
    user_exists = ""
    user_exists = mongo.db.User.find_one({'Email' : Payload["Email"]})
    if user_exists:
        #Error if user exists
        return jsonify({
            "Success" : False, 
            "Message" : "User Already Exists"
        }), 201
    else:
        #If user does not exist
        Payload["Password"] = bcrypt.generate_password_hash(Payload["Password"]).decode('utf-8')
        #new_user = usertest(username = Payload["Email"], password = Payload["Password"])
        #create new user object and insert it into mongodb
        # new_user = json.dumps(new_user.__dict__)
        # new_user = json.loads(new_user)
        diaryEntry = mongo.db.User.insert_one(username = Payload["Email"], password = Payload["Password"])
        return jsonify({"Success": True})




if __name__ == "__main__":
    # Running the flask app
    # This previous setting enables SSL - commented out in the current file
    #app.run(host="0.0.0.0", ssl_context='adhoc')
    app.run()
