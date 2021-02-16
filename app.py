from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from tempfile import mkdtemp
import pycountry
import os
import psycopg2
import psycopg2.extras

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# config sql db
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.autocommit = True

db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    countries = pycountry.countries

    if request.method == "POST":
        username = str(request.form.get("username"))
        country = str(request.form.get("country"))
        birth_year = int(request.form.get("birth_year"))
        password = str(request.form.get("password"))
        password_conf = str(request.form.get("confirmation"))

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)
        if len(username) > 40:
            return apology("username must be <= 40 chars long", 400)

        # Ensure BY was submitted
        if not birth_year:
            return apology("must provide username", 400)
        if birth_year < 1920 or birth_year > 2020:
            return apology("invalid birth year", 400)

        # check country list
        # if not country in countries:
        #    return apology("invalid country", 400)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)
        if password != password_conf:
            return apology("passwords must match", 400)

        # Query database for username
        db.execute("SELECT * FROM dim_user WHERE username = %s", (username, ))
        rows = db.fetchall()

        # Ensure username does not exist
        if len(rows) != 0:
            return apology("user already exists", 400)
        else:
            db.execute("INSERT INTO dim_user (username, birth_year, country, password_hash) VALUES(%s, %s, %s, %s)",
                       (username, birth_year, country, generate_password_hash(password,)))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", countries=countries)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = str(request.form.get("username"))
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        db.execute("SELECT * FROM dim_user WHERE username = %s", (username, ))
        rows = db.fetchall()

        pw_hash = rows[0]["password_hash"]
        pw_form = str(request.form.get("password"))
        if len(rows) == 0:
            return apology("no such user", 403)

        # Ensure username exists and password is correct
        if not check_password_hash(pw_hash, pw_form):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = username

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
