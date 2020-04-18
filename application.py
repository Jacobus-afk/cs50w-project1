import os

from flask import Flask, session, redirect, request, render_template, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import requests

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

@app.route("/api/<string:isbn>")
def book_api(isbn):
    query = ("SELECT id, isbn, title, author, year FROM books WHERE isbn=:isbn")
    book = db.execute(query, {"isbn": isbn}).fetchone()
    if not book:
        return "404 Error! ISBN number not in database", 404
    query = ("SELECT rating, review FROM reviews WHERE book_id=:b_id")
    reviews = db.execute(query, {"b_id": book.id}).fetchall()
    review_count = len(reviews)
    average_score = 0.0
    for entry in reviews:
        average_score += entry.rating
    if average_score:
        average_score /= review_count

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": review_count,
        "average_score": f"{average_score:.1f}"
    })

@app.route("/")
@login_required
def index():
    #flash(session["uid"],"info")
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        uname = request.form.get("username")
        pwd = request.form.get("password")
        if not uname or not pwd:
            flash("Username or password entries can't be blank","info")
            return render_template("login.html")
        req = db.execute("SELECT * FROM users WHERE username = :un", {"un": uname}).fetchone()

        if not req  or not check_password_hash(req.hash, pwd):
            flash("Invalid username and/or password", "error")
            return render_template("login.html")
        session["uid"] = req.id
        return redirect("/")
    
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        uname = request.form.get("username")
        pwd = request.form.get("password")

        if not uname or not pwd:
            flash("Username or password entries can't be blank","info")
            return render_template("register.html")

        hash = generate_password_hash(pwd)
        try:
            db.execute("INSERT INTO users (username,hash) VALUES(:un, :h)", {"un": uname, "h":hash})
            db.commit()
        except Exception as e:
            if "already exists" in str(e):
                flash("Username already exists in database. Please choose a different one", "info")
                return render_template("register.html")
            print(e)

        id = db.execute("SELECT id FROM users WHERE username = :un", {"un": uname}).fetchone()
        session["uid"] = id[0]
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        book = request.form.get("searchbook")
        if not book:
            flash("Blank search query", "info")
            return render_template("search.html")
        wc_book_wc = "%{}%".format(book.lower())
        query = ("SELECT id, isbn, title, author, year FROM books WHERE "
                "LOWER(title) LIKE :tq "
                "OR LOWER(author) LIKE :tq "
                "OR LOWER(isbn) LIKE :tq")
        resp = db.execute(query ,{"tq": wc_book_wc}).fetchall()
        if not resp:
            flash("Sorry, nothing found", "info")
            return render_template("search.html")
        session["book_list"] = resp
        return render_template("books.html", book_list=resp)
        #return redirect("/")
    else:
        return render_template("search.html")

@app.route("/book/<string:isbn>")
@login_required
def book(isbn):
    book = next((entry for entry in session["book_list"] if entry["isbn"] == isbn), None)
    if book:
        session["current_book"] = book
        query = ("SELECT * FROM reviews WHERE book_id=:id AND user_id=:uid")
        own_review = db.execute(query, {"id": book.id, "uid": session["uid"]}).fetchone()
        query = ("SELECT * FROM reviews WHERE book_id=:id AND user_id!=:uid")
        other_reviews = db.execute(query, {"id": book.id, "uid": session["uid"]}).fetchall()

        #if not resp:
        #    flash("No reviews yet", "info")
        #if resp:
            #own_review = next((entry for entry in resp if entry["user_id"] == session["uid"]), None)
        #flash(other_reviews, "info")
        query = ("https://www.goodreads.com/book/review_counts.json")
        params = {"key": "01RIlNJQxWp7QLLXGUeVEQ", "isbns": book.isbn}
        resp = requests.get(query, params = params)
        goodread_data = resp.json()["books"][0]
        avg_rating = goodread_data["average_rating"]
        rating_cnt = goodread_data["work_ratings_count"]
        stars = int(float(avg_rating) + 0.5)
        #flash("test","info")
        return render_template("book.html", book_info = book, own_review = own_review, other_reviews = other_reviews, \
            gr_stars = stars, gr_avg = avg_rating, gr_cnt = rating_cnt)
    else:
        flash("Error! Couldn't find book", "error")
        return render_template("index.html")

@app.route("/review", methods=["GET", "POST"])
@login_required
def review():
    if request.method == "POST":
        rating = request.form.get("rating")
        review = request.form.get("review")
        if not rating or not review:
            flash("Please write a review and select a rating for the book", "error")
            return redirect(f"/book/{session['current_book'].isbn}")

        query = ("INSERT INTO reviews (rating, review, user_id, book_id) "
                "VALUES (:rating, :review, :uid, :bid)")
        db.execute(query, {"rating": rating, "review": review, "uid": session["uid"], "bid": session["current_book"].id})
        db.commit()
        flash("Your review was submitted", "info")
        return redirect(f"/book/{session['current_book'].isbn}")
    else:
        return redirect("/")



