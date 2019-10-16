from mongoengine import *


class DiaryEntries(Document):
    title = StringField(max_length=200)
    body = StringField(max_length=10000)
    entryDate = StringField(max_length=50)
    updateTS = StringField(max_length=50)
    userID = StringField(max_length=50)
