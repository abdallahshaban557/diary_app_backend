import time
import json
from flask import Flask, request, Response, jsonify
from flask_pymongo import PyMongo
from functools import wraps
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://root:password1@ds151086.mlab.com:51086/diary_app"
mongo = PyMongo(app)

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


@app.route('/')
def hello():
    diary_entry = mongo.db.diary_entries.find_one({'test': 'tesdsds'})
    # figure out how to make this work
    test = mongo.db.diary_entries.find().sort("entryDate", -1).limit(50)#.skip()
    print(test[0])
    return jsonify({"Success": diary_entry['test']})


@app.route('/getAllEntries')
def getAllEntries():
    entries = []
    Payload = request.json
    # figure out how to make this work
    for x in mongo.db.diary_entries.find().sort("entryDate", -1).limit(5).skip(Payload["skip"]):
        print(x)
        entries.append(
            {
                "_id" : str(x["_id"]),
                "title" : x["title"],
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
def editEntry():
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
                "entryDate" : Payload["entryDate"],
                "body": Payload["body"],
                "updateTS": current_Datetime
            }
        }
    )
    return jsonify({"Success": True})

if __name__ == "__main__":
    # Running the flask app
    # This previous setting enables SSL - commented out in the current file
    #app.run(host="0.0.0.0", ssl_context='adhoc')
    app.run()
