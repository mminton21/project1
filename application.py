import os

from flask import Flask, session, request, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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


@app.route("/")
def index():
    return "Project 1: TODO"

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html', foo='42')
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
      session['username'] = request.form['username']
      return redirect(url_for('index'))
