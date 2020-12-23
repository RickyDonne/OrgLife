import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

app= Flask (__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db=SQL("sqlite:///project.db")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/home")
@login_required
def index():
    num = db.execute("SELECT COUNT(*) AS NUM FROM todo WHERE user_id=:user_id", user_id=session["user_id"])
    rows = db.execute("SELECT username FROM users WHERE id = :user_id",
        user_id=session["user_id"])
    name=rows[0]["username"]
    table = db.execute("SELECT * FROM todo WHERE user_id = :user_id", user_id=session["user_id"])
    return render_template("index.html",num=num,  name=name, table=table)

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()
    if request.method == "POST":

        if not request.form.get("username"):
            return render_template("apology.html", message="must provide username")

        elif not request.form.get("password"):
            return render_template("apology.html", message="must provide password")

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", message="invalid username and/or password")
        session["user_id"] = rows[0]["id"]
        return redirect("/home")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        if not request.form.get("username"):
            return render_template("apology.html", message="must provide username")

        elif not request.form.get("password"):
            return render_template("apology.html", message="must provide password")

        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("apology.html", message="passwords didn't match")

        elif db.execute("SELECT * FROM users WHERE username = :username",
            username = request.form.get("username")):
            return render_template("apology.html", message="username already exists")

        db.execute("INSERT INTO users(username, hash) VALUES (:username, :hash)",
            username = request.form.get("username"),
            hash=generate_password_hash(request.form.get("password")))

        rows = db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username"))

        session["user_id"] = rows[0]["id"]

        return redirect("/home")

    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/home")

@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        task = request.form.get("task")

        if not task:
            return render_template("apology.html", message="task can not be empty")

        db.execute("INSERT INTO todo(user_id, task) VALUES (:user_id, :task)", user_id=session["user_id"], task = task)
        return redirect("/home")

    else:
        return render_template("add.html")

@app.route("/delete/<int:task_id>")
def delete(task_id):
    db.execute("DELETE FROM todo WHERE id=:task_id", task_id = task_id)
    return redirect("/home")

@app.route("/about")
def about():
    return render_template("about.html")
