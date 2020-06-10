import os

from flask import Flask, session, request, render_template, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

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


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        query = request.form['squery']
        selector = request.form.get('squery_type')
        selector = str(selector)
        query = query + "%"

        if selector == 'isbn':
            search = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": query}).fetchall()
 
        if selector == 'author':
            search = db.execute("SELECT * FROM books WHERE author LIKE :author", {"author": query}).fetchall()

        if selector == 'title':
            search = db.execute("SELECT * FROM books WHERE title LIKE :title", {"title": query}).fetchall()

        slen = len(search)
        if slen == 0:
            return render_template("error.html", message="Sorry, that search yielded no results.")


        return render_template('index.html', search=search)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    else:
        u = request.form['username']
        p = request.form['password']

        username_checker = db.execute("SELECT username FROM users WHERE username = :username", {"username": u}).fetchall()
        if username_checker:
            return render_template("error.html", message="Sorry, that username is already taken.")


        db.execute("INSERT INTO users (username, password) VALUES (:username, crypt(:password, gen_salt('bf', 8)))", {"username": u, "password": p})
        db.commit()

        return render_template('login.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
      u = request.form['username']
      p = request.form['password']
      accuracy_checker = db.execute("SELECT * FROM users WHERE username = :username AND password = crypt(:password, password)", {"username": u, "password": p}).fetchall()

      if accuracy_checker:
          session["user_id"] = accuracy_checker[0]["user_id"]
          return redirect(url_for('index'))
      else:
          return render_template("error.html", message="Sorry, that information is inaccurate.")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/<isbn>", methods=['GET', 'POST'])
def book_isbn(isbn):
    if request.method == 'POST':
        rating = request.form.get('book_rating')
        comment = request.form['text']
        user_id = str(session['user_id'])

        elig_checker = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND isbn = :isbn", {"user_id": user_id, "isbn": isbn})
        if elig_checker.rowcount >= 1:
            return render_template('error.html', message="Sorry, only one review per person per book.")

        db.execute("INSERT INTO reviews (rating, comment, isbn, user_id) VALUES (:rating, :comment, :isbn, :user_id)", {"rating": rating, "comment": comment, "isbn": isbn, "user_id": session["user_id"]})
        db.commit()
        return redirect(url_for('thanks'))
    
    if request.method == 'GET':
        isbn_f = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
        reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "BrqUT8gVYRCu6yqFUDFHvA", "isbns": isbn})
        content = res.json()
        
        av_rating = content["books"][0]['average_rating']
        count = content["books"][0]['work_ratings_count']

        return render_template('book.html', isbn_f = isbn_f, reviews=reviews, content=content, av_rating=av_rating, count=count)

@app.route("/thanks", methods=['GET', 'POST'])
def thanks():
    return render_template('thanks.html', message="Thanks for submitting!")

@app.route("/api/<isbn>")
def api(isbn):

    #Get Info
    listtojson = db.execute("SELECT title, author, year, books.isbn, COUNT(reviews.rating) FROM books INNER JOIN reviews ON books.isbn = reviews.isbn WHERE books.isbn = :isbn GROUP by title, author, year, books.isbn", {"isbn": isbn}).fetchall()
    
    if listtojson:

        ljson = listtojson[0]
        title = ljson[0]
        author = ljson[1]
        year = ljson[2]
        isbn_json = ljson[3]
        review_count= ljson[4]
    
        avg = db.execute("SELECT rating FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        counter = 0
        total = 0
        rate = []
        for rating in avg:
            rate.append(rating[0])

        for r in rate:
            total += int(r)
            counter += 1

        if counter == 0:
            rating_average = "N/A"
        else:
            rating_average = float(total) / counter
            rating_average = format(rating_average, '.2f')

        return jsonify({
            "title": title,
            "author": author,
            "year": year,
            "isbn": isbn_json,
            "rating_average": rating_average,
            "review_count": review_count
        })

    else:
        return jsonify({"error": "Invalid isbn"}), 404



