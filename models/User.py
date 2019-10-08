from mongoengine import *

class User(Document):
    username = StringField(max_length=200)
    password = StringField(max_length=200)
    firstName = StringField(max_length=50)
    lastName = StringField(max_length=50)
    gender = StringField(max_length=2)
    dateOfBirth = StringField(max_length=50)
    signInType = StringField(max_length=2)