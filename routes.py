##################################################################
# routes
##################################################################


# import external dependancies
from flask import render_template, jsonify, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import re

# import my own modules
from app import app, login_required, months
from dbModels import Users, Contacts, Events, db


# Render events page
@app.route("/")
@login_required
def events():
    """Render events page"""

    # filter the events by the year passed in by the user

    # retrieve all events from database
    events = Events.query.order_by(Events.date).all()

    # prep
    list_items = ["", ]
    prev_date = ""
    index = 0 # 'current working index' or 'cwi'
    month_headers = [True, False, False, False, False, False, False, False, False, False, False, False, False]


    # -------------------------------------------------------------------------------------------------------------------------------
    # iterating over each event
    # parse the data: create an element on the array for every day that has one or more events
    # (each element will be an HTML list item)
    # -------------------------------------------------------------------------------------------------------------------------------
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
        # this will create an '<a>' element for each event
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

        # iteration over each event ends ---------------------------------------------------------------------------------------------

    # pass data to events.html
    return render_template("events.html", list_items=list_items)





# Render directory page
@app.route("/directory")
@login_required
def directory():
    """Render directory page"""

    # get all contacts and render them on the directory page
    contacts = Contacts.query.order_by(Contacts.last_name).all()
    return render_template("directory.html", contacts=contacts)




# Add or edit an event
# (what's REST anyways?)
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

    # format and save date
    currentYear = datetime.datetime.now().year
    try:
        date = datetime.date(currentYear, month_num, day_num)
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




# Delete an event
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




# Register user
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
        return render_template("messages.html", code='Success' , message="Thanks for registering, your info is saved, and you will be able to login as soon as you are approved. If you haven't yet, contact Kenneth so he can give you access."), 200

    else:
        # render page via which user can register
        return render_template("register.html")




#---------------------------------------------------------------------------------------------------------------------
# part of the routes below were written by CS50 staff
#---------------------------------------------------------------------------------------------------------------------
# Log user in
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




# Log user out
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user id
    session.clear()

    # Redirect user to login form
    return redirect("/login")
