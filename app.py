import os
from flask import Flask, render_template, jsonify, request, redirect, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import re


app = Flask(__name__)



# require app to always redirect to https
@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


# CS50 staff code -------------------------------------------------------------------------------
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
# CS50 staff code -------------------------------------------------------------------------------


# configure client side sessions using cookies
app.config["SECRET_KEY"] = "J#7KazuNps/k8U2z"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=90)


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

    def __init__(self, first_name, last_name, phone, email, addr_line1, addr_line2, city, state, postal):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
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


# Global variable
months = ["","January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


# CS50 staff code here -------------------------------------------------------------------------------
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
# CS50 staff code here -------------------------------------------------------------------------------------




@app.route("/")
@login_required
def events():
    """Render events page"""

    # retrieve all events from database
    events = Events.query.order_by(Events.date).all()

    # prep
    list_items = ["", ]
    prev_date = ""
    index = 0 # 'current working index' or 'cwi'
    month_headers = [True, False, False, False, False, False, False, False, False, False, False, False, False]


    # iterating over each event----------------------------------------------------------------------------------------------------------
    # parse the data: create an element on the array for every day that has one or more events
    # (each element will be an HTML list item)
    for event in events:

        # if the current month has not yet been appended to the array (will be a header on the page)
        if month_headers[event.month_num] == False:
            if event.month_num != 1: # if this is not the first element of the array (i.e. January heading):
                list_items[index] += "</li>" # append a closing '<li>' for the last item

            # append the month heading to the array
            list_items.append(f"<li class='list-group-item ev_li-month col-lg-7 col-md-8 col-sm-10 col-11' id='{months[event.month_num]}'><h3 class='month'>{months[event.month_num]}</h3>")
            month_headers[event.month_num] = True

        index = (len(list_items) - 1) # calculate 'cwi'

        # unless the the current event is on the same day as the last one, create a new element on the array for it
        # this will create an '<li>' element for each day with one or more events
        if event.date != prev_date:
            list_items[index] += "</li>"
            list_items.append(f"<li class='list-group-item allev_li col-lg-7 col-md-8 col-sm-10 col-11'><time class='ev_li_date' datetime='{event.date}'>{event.readable_date}</time>")

        index = (len(list_items) - 1) # calculate 'cwi'

        # append current event to the 'cwi' of the array
        # this will create an '<a>' element for each event (inside the '<li>')
        list_items[index] += f"<a href='#' name='{event.type}' class='allev_btn' id='{event.id}' role='button' data-toggle='popover' tabindex='0'><h6 class='ev_li_h6'>{event.title}"
        if event.type == "anniversary":
            list_items[index] += " <i class='fas fa-heart'></i></h6>"
        elif event.type == "birthday":
            list_items[index] += " <i class='fas fa-birthday-cake'></i></h6>"
        elif event.type == "event":
            list_items[index] += " <i class='far fa-calendar-alt'></i></h6>"
        elif event.type == "food":
            list_items[index] += " <i class='fas fa-utensils'></i></h6>"
        if event.time:
            time = event.time.strftime("%I:%M %p") # format to 12 hr time
            list_items[index] += f"<time class='ev_li_time' datetime='{event.time}'>{time}</time>"
        if event.location:
            list_items[index] += f"<div class='ev_li_location'>{event.location}</div>"
        if event.notes:
            list_items[index] += f"<p class='ev_li_notes'>{event.notes}</p>"
        list_items[index] += "</a>"

        # save the current event date for the next iteration of the loop
        prev_date = event.date
        # iterating over each event-----------------------------------------------------------------------------------------------------

    # pass data to events.html
    return render_template("events.html", list_items=list_items)




@app.route("/directory")
@login_required
def directory():
    """Render directory page"""

    # save all contacts in temp
    contacts = Contacts.query.order_by(Contacts.last_name).all()

    # pass data to directory.html
    return render_template("directory.html", contacts=contacts)




@app.route("/addev", methods=["POST"])
@login_required
def addev():
    """Add or edit an event"""

    # validating, formatting, and saving the data------------------------------------------------------------------------------------

    # check if required info is present, if so, save that data
    if not request.form.get("title") or not request.form.get("type") or not request.form.get("month_num") or not request.form.get("day_num"):
        return "Sorry, required info is missing", 400

    # ensure the essential data is correctly formatted
    title = request.form.get("title")
    type = request.form.get("type")
    try:
        month_num = int(request.form.get("month_num"))
        day_num = int(request.form.get("day_num"))
        event_id = int(request.form.get('event_id'))
    except ValueError:
        return "Sorry, there's something wrong with the data format.", 400

    # check the rest of the data and save if present
    time, location, notes = None, None, None
    if request.form.get("time"):
        time = request.form.get("time")
    if request.form.get("location"):
        location = request.form.get("location")
    if request.form.get("notes"):
        notes = request.form.get("notes")

    # format and save 'date' (only current year allowed for now)
    cur_year = 2018
    try:
        date = datetime.date(cur_year, month_num, day_num)
    except (ValueError, TypeError):
        return "Sorry, this date isn't valid. Make sure you didn't select something like: 'February 30'", 400

    # format and save 'readable_date'
    weeks = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wkday = weeks[date.weekday()]
    month_name = months[month_num]
    readable_date = f"{wkday}, {month_name} {day_num}"

    # validating, formatting, and saving the data------------------------------------------------------------------------------------

    # if this is a new event:
    # ('event_id' is a hidden, pre-initialized input in the form)
    if event_id == 0:
        new_ev = Events(title, date, time, readable_date, location, notes, type, month_num)
        db.session.add(new_ev)
        db.session.commit()
        return "Success", 200
    else:
        # if this is an existing event:
        # ('event_id' here is a hidden input in the form that is pre-initialized as the event id in the database)
        if db.session.query(db.exists().where(Events.id == event_id)).scalar(): # this is stock SQLAlchemy
            event = Events.query.get(event_id)
            event.title = title
            event.date = date
            event.time = time
            event.readable_date = readable_date
            event.location = location
            event.notes = notes
            event.type = type
            event.month_num = month_num
            db.session.commit()
            return "Success", 200




@app.route("/delev", methods=["POST"])
@login_required
def delev():
    """Delete an event"""
    # obtain event to be deleted
    event_id = request.form.get('id')

    # delete event if it exists
    event = Events.query.filter_by(id=event_id).first()
    if event:
        db.session.delete(event)
        db.session.commit()
        return "operation successful", 200
    else:
        return "Sorry, something went wrong", 500




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user id
    session.clear()

     # if user submitted register request:
    if request.method == "POST":

        # check if username and password were submitted
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("messages.html", code=400 , message="Please provide username and password"), 400

        # check if name submitted
        elif not request.form.get("first_name"):
            return render_template("messages.html", code=400 , message="Please provide name"), 400

         # check if password matches requirements
        elif len(request.form.get("password")) < 8 or len(request.form.get("password")) > 16 or not re.search('[0-9]', request.form.get("password")) or not re.search('[a-zA-Z]', request.form.get("password")):
            return render_template("messages.html", code=400 , message="Password must contain 8-16 characters, with at least one number and one letter"), 400

        # check if username already exists in database
        exists = Users.query.filter_by(username=request.form.get("username")).first()
        if exists:
            return render_template("messages.html", code=400 , message="Sorry, that username is taken, please choose something else"), 400

        # store all user info in database, initialize approval to False
        first_name = request.form.get("first_name")
        username = request.form.get("username")
        pwd_hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        approval = False
        new_user = Users(first_name, username, pwd_hash, approval)
        db.session.add(new_user)
        db.session.commit()

        # ensure user was saved to database
        user = Users.query.filter_by(username=username).first()
        if not user:
            return render_template("messages.html", code=500 , message="Sorry, something went wrong on the server, we couldn't save your info"), 500

        # send message telling user to wait for approval
        # javascript will 'redirect' to another page and display message
        return render_template("messages.html", code='Success' , message="Thanks for registering, your info is saved, and you will be able to login as soon as you are approved. If you haven't yet, let Kenny know you registered so he can give you access."), 200

    else:
        # render page via which user can register
        return render_template("register.html")




# partly CS50 staff code below --------------------------------------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user id
    session.clear()

    # if user submitted a login form:
    if request.method == "POST":

        # Ensure username and password were submitted
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("messages.html", code=400, message="Please provide username and password"), 400

        username = request.form.get("username")

        # Query database for username
        user = Users.query.filter_by(username=username).first()
        if not user:
            return render_template("messages.html", code=400, message="Sorry, invalid username"), 400

        # Ensure password is correct
        elif not check_password_hash(user.pwd_hash, request.form.get("password")):
            return render_template("messages.html", code=400, message="Sorry, invalid password"), 400

        # Ensure user is approved
        elif user.approval != True:
            return render_template("messages.html", code=403, message="Sorry, doesn't look like you've been approved yet."), 403

        # Remember which user has logged in
        session["user_id"] = user.id
        session.permanent = True

        # Redirect to events page
        return redirect("/")

    else:
        # render login page
        return render_template("login.html")




@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user id
    session.clear()

    # Redirect user to login form
    return redirect("/login")
