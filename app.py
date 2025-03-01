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
import json

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session
app.secret_key = os.getenv("SECRET_KEY")

# config sql db
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.autocommit = True
db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Ensure responses aren't cached

# read promoted content file
with open('static/promoted.json', 'r') as myfile:
    data=myfile.read()
promoted = json.loads(data)


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    
    sql_exec = "SELECT                                                           " \
            "       DF.name AS impact_factor                                         " \
            "     , SUM(FAFFW.impact_weight * FAFFW.frequency_weight) AS Footprint   " \
            " FROM public.fact_quiz_answers QA                                       " \
            " INNER JOIN public.fact_activity_factor_freq_weights FAFFW              " \
            " ON 1=1                                                                 " \
            "     AND QA.activity_id = FAFFW.activity_id                             " \
            "     AND QA.frequency_id = FAFFW.frequency_id                           " \
            " INNER JOIN public.dim_impact_factors DF                                " \
            " ON 1=1                                                                 " \
            "     AND DF.id = FAFFW.impact_factor_id                                 " \
            " WHERE 1=1                                                              " \
            " GROUP BY DF.name                                                       " \
            " ORDER BY Footprint DESC                                                " \
            "     ;                                                                  "
    
    # if logged in...
    if session:
        sql_exec = sql_exec.replace("WHERE 1=1","WHERE QA.user_id = %s")
        db.execute(sql_exec, (session["user_id"],))
        rows = db.fetchall()

        # check quiz has been done
        if len(rows) != 0:
            quizitems = []

            for row in rows:
                quizitems.append(
                    {"impact_factor": row["impact_factor"], "footprint": row["footprint"]})

            return render_template("index.html", quizitems=quizitems)
        else:
            return render_template("index.html")
    else:
        sql_exec = sql_exec.replace(" AS Footprint","/COUNT(DISTINCT user_id) AS Footprint")
        db.execute(sql_exec)
        rows = db.fetchall()

        quizitems = []
        for row in rows:
            quizitems.append(
                {"impact_factor": row["impact_factor"], "footprint": int(row["footprint"])})

        return render_template("index.html", quizitems=quizitems, promoted=promoted)
        
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    countries = pycountry.countries

    if request.method == "POST":
        username = str(request.form.get("username"))
        country = str(request.form.get("country"))
        birth_year = request.form.get("birth_year")
        password = str(request.form.get("password"))
        password_conf = str(request.form.get("confirmation"))

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)
        if len(username) > 40:
            return apology("username must be <= 40 chars long", 400)
        if " " in username:
            return apology("spaces are not allowed in username", 400)

        # Ensure BY was submitted
        if not birth_year:
            return apology("must provide username", 400)
        else:
            birth_year = int(birth_year)

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

        if len(rows) == 0:
            return apology("no such user", 403)

        pw_hash = rows[0]["password_hash"]
        pw_form = str(request.form.get("password"))

        # Ensure username exists and password is correct
        if not check_password_hash(pw_hash, pw_form):
            return apology("check username and password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = username

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to main
    return redirect("/")


@app.route("/change_pwd",  methods=["GET", "POST"])
@login_required
def change_pwd():
    if request.method == "POST":
        password = str(request.form.get("password"))
        password_conf = str(request.form.get("confirmation"))

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)
        if password != password_conf:
            return apology("passwords must match", 400)

        db.execute("UPDATE dim_user SET password_hash = %s WHERE username = %s",
                   (generate_password_hash(password), session["username"], ))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_pwd.html")


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    """Quiz"""
    if request.method == "GET":

        quizitems = []
        db.execute("SELECT * FROM dim_activity")
        rows = db.fetchall()

        for row in rows:
            quizitems.append(
                {"id": row["id"], "question": row["name"], "description": row["description"]})

        frequencyitems = []
        db.execute("SELECT * FROM dim_frequency")
        rows = db.fetchall()

        for row in rows:
            frequencyitems.append({"id": row["id"], "name": row["name"]})

        return render_template("quiz.html", quizitems=quizitems, frequencyitems=frequencyitems)

    if request.method == "POST":
        # update databases
        sql_exec = "INSERT INTO fact_quiz_answers (user_id, activity_id, frequency_id)" \
            "	VALUES (%s, %s , %s) " \
            "	ON CONFLICT (user_id, activity_id)  DO UPDATE SET frequency_id = EXCLUDED.frequency_id" \

        quizreplies_form = request.form
        for key, value in quizreplies_form.items():
            #print(key, value)
            db.execute(sql_exec, (session["user_id"], key, value,))

        return redirect("/")
