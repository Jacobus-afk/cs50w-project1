import os

from flask import Flask, session, redirect, request, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
#import requests

#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "01RIlNJQxWp7QLLXGUeVEQ", "isbns": "9781632168146"})
#print(res.json())

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#https://flask.palletsprojects.com/en/1.0.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("uid") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    print("test")
    return "Test"

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        pass
    else:
        return render_template("login.html")
    
