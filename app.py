from flask import Flask, session, redirect
from functools import wraps
import datetime
import os

app = Flask(__name__)

from dbModels import Users, Contacts, Events



# configure client side sessions using cookies
app.config["SECRET_KEY"] = os.environ['SECRET_KEY']
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=90)


## require app to always redirect to https
# @app.before_request
# def before_request():
#     if request.url.startswith('http://'):
#         url = request.url.replace('http://', 'https://', 1)
#         code = 301
#         return redirect(url, code=code)


# Middleware from Harvard's CS50 staff code ---------------------------------------------------
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Decorate routes to require login.
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
# Middleware from Harvard's CS50 staff code ----------------------------------------------------


# Global variable
months = ["","January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


# ROUTES
import routes
