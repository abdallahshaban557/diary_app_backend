#script to add userID to the diaryEntry documents.

import pymongo
import os
from pymongo import MongoClient

#Connect to Client
client = MongoClient(os.environ['DB_URI_PROD'])
#Find DB Name/Then Collection/Then mass update
DB = client.diary_app
diaryEntryCollection = DB.diary_entries
diaryEntryCollection.update_many({},{"$set": { "userID": "5da135447c213e55613df0d6" }})

