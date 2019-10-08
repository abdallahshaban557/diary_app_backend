#script to add userID to the diaryEntry documents.

import pymongo
import os
from pymongo import MongoClient

#Connect to Client
client = MongoClient(os.environ['DB_URI'])
#Find DB Name/Then Collection/Then mass update
DB = client.diary_app_dev
diaryEntryCollection = DB.diary_entry
diaryEntryCollection.update_many({},{"$set": { "userID": "Canyon_12345" }})

