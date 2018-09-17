##################################################################
# routes
##################################################################


# import external dependancies
from flask import render_template, jsonify, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import and_
import datetime
import re
import jsonpickle

# import my own modules
from app import app, login_required, months, weeks
from dbModels import Users, Contacts, Events, db


# redirect home page to events page
@app.route("/", methods=["GET"])
@login_required
def redir():
    """Redirect to Events Page"""
    return redirect("/events", 302)


# SHOW events page
@app.route("/events", methods=["GET"])
@app.route("/events/<int:year>", methods=["GET"])
@login_required
def events(year=datetime.datetime.now().year):
    """Render events page"""

    yearBegin = datetime.date(int(year), 1, 1)
    yearEnd = datetime.date(int(year), 12, 31)

    # retrieve all events from database
    events = Events.query.filter(and_(Events.date >= yearBegin, Events.date <= yearEnd)).order_by(Events.date).all()

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
        elif event.type == "event" or event.type == "holiday":
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
    currentYear = datetime.datetime.now().year
    years = [(currentYear -1), currentYear, (currentYear + 1)]

    # pass data to events.html
    return render_template("events.html", list_items=list_items, years=years, year=year)






# ADD an event
@app.route("/events", methods=["POST"])
@login_required
def addev():
    """Add an event"""

    # ensure required data is present
    if not request.form.get("title") or not request.form.get("type") or not request.form.get("date"):
        return "Sorry, required info is missing", 400

    # ensure the essential data is correctly formatted
    title = request.form.get("title")
    type = request.form.get("type")
    try:
        month_num = int(request.form.get("date")[:2])
        day_num = int(request.form.get("date")[3:5])
        year_num = int(request.form.get("date")[6:])
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

    # format date
    try:
        date = datetime.date(year_num, month_num, day_num)
    except (ValueError, TypeError):
        return "Sorry, this date isn't valid.", 400

    # format 'readable_date'
    wkday = weeks[date.weekday()]
    month_name = months[month_num]
    readable_date = f"{wkday}, {month_name} {day_num}"

    # save the event to the database
    new_ev = Events(title, date, time, readable_date, location, notes, type, month_num)
    db.session.add(new_ev)
    db.session.commit()
    return "Success", 200





# EDIT an event
@app.route("/events/<event_id>", methods=["PUT"])
@login_required
def editev(event_id):
    """Edit an event"""

    # ensure required data is present
    if not request.form.get("title") or not request.form.get("type") or not request.form.get("date"):
        return "Sorry, required info is missing", 400

    # ensure the essential data is correctly formatted
    title = request.form.get("title")
    type = request.form.get("type")
    try:
        month_num = int(request.form.get("date")[:2])
        day_num = int(request.form.get("date")[3:5])
        year_num = int(request.form.get("date")[6:])
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

    # format date
    try:
        date = datetime.date(year_num, month_num, day_num)
    except (ValueError, TypeError):
        return "Sorry, this date isn't valid.", 400

    # format 'readable_date'
    wkday = weeks[date.weekday()]
    month_name = months[month_num]
    readable_date = f"{wkday}, {month_name} {day_num}"


    # save the event to the database
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





# DELETE an event
@app.route("/events/<int:event_id>", methods=["DELETE"])
@login_required
def delev(event_id):
    """Delete an event"""

    # delete event if it exists
    event = Events.query.filter_by(id=event_id).first()
    if event:
        db.session.delete(event)
        db.session.commit()
        return "", 200
    else:
        return "Sorry, something went wrong", 500






# SHOW directory page
@app.route("/directory", methods=["GET"])
@login_required
def directory():
    """Render directory page"""

    # get all contacts and render them on the directory page
    contacts = Contacts.query.order_by(Contacts.last_name).all()
    return render_template("directory.html", contacts=contacts)




# ADD an contact
@app.route("/directory", methods=["POST"])
@login_required
def addcontact():
    """Add a contact"""
    # ensure required data is present
    if not request.form.get("firstName") or not request.form.get("lastName") or not request.form.get("phone0") or not request.form.get("addrLine0") or not request.form.get("city") or not request.form.get("state") or not request.form.get("postal"):
        return "Sorry, required info is missing", 400

    # get the essential data
    firstName = request.form.get("firstName")
    lastName = request.form.get("lastName")
    phone0 = request.form.get("phone0")
    addrLine0 = request.form.get("addrLine0")
    city = request.form.get("city")
    state = request.form.get("state")
    postal = request.form.get("postal")

    # get the rest of the data if present
    phone1, addrLine1, email = None, None, None
    if request.form.get("phone1"):
        phone1 = request.form.get("phone1")
    if request.form.get("addrLine1"):
        addrLine1 = request.form.get("addrLine1")

    newContact = Contacts(firstName, lastName, phone0, phone1, email, addrLine0, addrLine1, city, state, postal)
    db.session.add(newContact)
    db.session.commit()
    return "", 200





# GET the data for the contact to be edited
@app.route("/directory/<int:contact_id>/edit", methods=["GET"])
@login_required
def showcontact(contact_id):
    """Get contact info"""
    contact = Contacts.query.filter_by(id=contact_id).first()

    temp = jsonpickle.encode(contact)
    return jsonify(temp)






# EDIT an contact
@app.route("/directory/<int:contact_id>", methods=["PUT"])
@login_required
def editcontact(contact_id):
    """Edit a contact"""
    # ensure required data is present
    if not request.form.get("firstName") or not request.form.get("lastName") or not request.form.get("phone0") or not request.form.get("addrLine0") or not request.form.get("city") or not request.form.get("state") or not request.form.get("postal"):
        return "Sorry, required info is missing", 400

    # get the essential data
    firstName = request.form.get("firstName")
    lastName = request.form.get("lastName")
    phone0 = request.form.get("phone0")
    addrLine0 = request.form.get("addrLine0")
    city = request.form.get("city")
    state = request.form.get("state")
    postal = request.form.get("postal")

    # get the rest of the data if present
    phone1, addrLine1, email = None, None, None
    if request.form.get("phone1"):
        phone1 = request.form.get("phone1")
    if request.form.get("addrLine1"):
        addrLine1 = request.form.get("addrLine1")


    # save the event to the database
    if db.session.query(db.exists().where(Contacts.id == contact_id)).scalar(): # this is stock SQLAlchemy
        contact = Contacts.query.get(contact_id)
        contact.first_name = firstName
        contact.last_name = lastName
        contact.phone0 = phone0
        contact.phone1 = phone1
        contact.addr_line1 = addrLine0
        contact.addr_line2 = addrLine1
        contact.city = city
        contact.state = state
        contact.postal = postal
        db.session.commit()
        return "Success", 200





# DELETE a contact
@app.route("/directory/<int:contact_id>", methods=["DELETE"])
@login_required
def delcontact(contact_id):
    """DELETE a contact"""

    # delete contact if it exists
    contact = Contacts.query.filter_by(id=contact_id).first()
    if contact:
        db.session.delete(contact)
        db.session.commit()
        return "", 200
    else:
        return "Sorry, something went wrong", 500






# SHOW the admin page
@app.route("/admin", methods=["GET"])
@login_required
def admin():
    """Render Admin Panel Page"""
    currentYear = datetime.datetime.now().year;
    years = [(currentYear -1), currentYear, (currentYear + 1)]
    return render_template("/admin.html", years=years)




# ADD events to new year from the admin page
@app.route("/admin/importevents", methods=["POST"])
@login_required
def importEvents():
    """Import Events to New Year"""

    # ensure required data is present
    if not request.form.get("type") or not request.form.get("newYear") or not request.form.get("oldYear"):
        return "Sorry, required info is missing", 400

    # ensure the essential data is correctly formatted
    type = request.form.get("type");
    try:
        newYear = int(request.form.get("newYear"))
        oldYear = int(request.form.get("oldYear"))
        yearBegin = datetime.date(oldYear, 1, 1)
        yearEnd = datetime.date(oldYear, 12, 31)
    except (ValueError, TypeError):
        return "Sorry, there's something wrong with the data format.", 400


    # find all the events of type 'type'
    events = Events.query.filter(and_(Events.type == type, Events.date >= yearBegin, Events.date <= yearEnd)).all()

    importedEventsCount = 0

    # iterate through each event
    for oldEvent in events:
        month_num = oldEvent.month_num
        day_num = oldEvent.date.day

        # construct the date
        try:
            date = datetime.date(newYear, month_num, day_num)
        except (ValueError, TypeError):
            return "This date isn't valid.", 400

        # construct the 'readable_date'
        wkday = weeks[date.weekday()]
        month_name = months[month_num]
        readable_date = f"{wkday}, {month_name} {day_num}"

        # save the event to the database
        new_ev = Events(oldEvent.title, date, oldEvent.time, readable_date, oldEvent.location, oldEvent.notes, oldEvent.type, oldEvent.month_num)
        db.session.add(new_ev)
        db.session.commit()
        importedEventsCount += 1


    return f"Imported {importedEventsCount}.", 200







# Register user
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user id
    session.clear()

     # if user submitted register request:
    if request.method == "POST":

        # check if username, password, and name were submitted
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("first_name"):
            return render_template("messages.html", code=400 , message="Missing required info"), 400

         # check if password matches requirements
        elif len(request.form.get("password")) < 8 or len(request.form.get("password")) > 16 or not re.search('[0-9]', request.form.get("password")) or not re.search('[a-zA-Z]', request.form.get("password")):
            return render_template("messages.html", code=400 , message="Password must contain 8-16 characters, with at least one number and one letter"), 400

        # check if username already exists in database
        exists = Users.query.filter_by(username=request.form.get("username")).first()
        if exists:
            return render_template("messages.html", code=400 , message="It looks like you already registered with that email, please sign in."), 400

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
            return render_template("messages.html", code=400, message="Please provide email and password"), 400

        # Query database for username
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if not user:
            return render_template("messages.html", code=400, message="Sorry, invalid email"), 400

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
@app.route("/logout", methods=["POST"])
def logout():
    """Log user out"""

    # Forget any user id
    session.clear()

    # Redirect user to login form
    return redirect("/login")
