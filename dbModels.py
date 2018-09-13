##################################################################
# configure database
##################################################################


import os
from flask_sqlalchemy import SQLAlchemy
from app import app

# Configure database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # the extension will track modifications if set to True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'] # assigning uri of database
db = SQLAlchemy(app) # creating the SQLAlchemy instance


# define class/model for users
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, unique=False, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    pwd_hash = db.Column(db.String, unique=False, nullable=False)
    approval = db.Column(db.Boolean, unique=False, nullable=False)

    def __init__(self, first_name, username, pwd_hash, approval):
        self.first_name = first_name
        self.username = username
        self.pwd_hash = pwd_hash
        self.approval = approval


# define class/model for Contacts
class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, unique=False, nullable=False)
    last_name = db.Column(db.String, unique=False, nullable=False)
    phone0 = db.Column(db.String, unique=False, nullable=False)
    phone1 = db.Column(db.String, unique=False, nullable=True)
    email = db.Column(db.String, unique=False, nullable=True)
    addr_line1 = db.Column(db.String, unique=False, nullable=False)
    addr_line2 = db.Column(db.String, unique=False, nullable=True)
    city = db.Column(db.String, unique=False, nullable=False)
    state = db.Column(db.String, unique=False, nullable=False)
    postal = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, first_name, last_name, phone0, phone1, email, addr_line1, addr_line2, city, state, postal):
        self.first_name = first_name
        self.last_name = last_name
        self.phone0 = phone0
        self.phone1 = phone1
        self.email = email
        self.addr_line1 = addr_line1
        self.addr_line2 = addr_line2
        self.city = city
        self.state = state
        self.postal = postal


# define class/model for Events
class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=False, nullable=False)
    date = db.Column(db.Date, unique=False, nullable=False)
    time = db.Column(db.Time, unique=False, nullable=True)
    readable_date = db.Column(db.String, unique=False, nullable=False)
    location = db.Column(db.String, unique=False, nullable=True)
    notes = db.Column(db.String, unique=False, nullable=True)
    type = db.Column(db.String, unique=False, nullable=False)
    month_num = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, title, date, time, readable_date, location, notes, type, month_num):
        self.title = title
        self.date = date
        self.time = time
        self.readable_date = readable_date
        self.location = location
        self.notes = notes
        self.type = type
        self.month_num = month_num
