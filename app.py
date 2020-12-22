import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env
# pip3 install Flask
# pip3 install flask-pymongo
# pip3 install dnspython


# Creating an instance of flask
app = Flask(__name__)

# Config to grab database
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

# Pymongo instance to add app using constructure method
mongo = PyMongo(app)


@app.route("/")
@app.route("/index")
def index():
    business = mongo.db.business.find()
    return render_template("index.html", results=business)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # checks if username exists in the db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # checks is password matches db
            if check_password_hash(
               existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))

            else:
                # if password does not match
                flash("Incorrect Username/Password")
                return redirect(url_for("login"))

        else:
            # if username does not match
            flash("Incorrect Username/Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # retrieves categories of business from db
    categories = mongo.db.category.find().sort("name", 1)

    if request.method == "POST":
        # checks if username already exists in the db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # checks if email already exists in the db
        existing_email = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        # verify email matches
        email_one = request.form.get("email")
        email_two = request.form.get("email2")

        # verify password matches
        password_one = request.form.get("password")
        password_two = request.form.get("password2")

        if existing_user or existing_email:
            flash("Username/Email already exists")
            return redirect(url_for("register"))

        elif email_one != email_two:
            flash("Emails must match to verify")
            return redirect(url_for("register"))

        elif password_one != password_two:
            flash("Passwords must match to verify")
            return redirect(url_for("register"))

        register_business = {
            "name": request.form.get("business_name"),
            "website": request.form.get("website"),
            "email": request.form.get("email").lower(),
            "address": request.form.get("address"),
            "category_name": request.form.get("business_type")
        }

        mongo.db.business.insert_one(register_business)

        register_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "business_id": register_business["_id"]
        }

        mongo.db.users.insert_one(register_user)

        # puts the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html", categories=categories)


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # retrieves session user's username from the db
    # [username] at the end selects that specific field from the user record.
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    business_id = list(mongo.db.business.find({"_id": mongo.db.users.find_one(
        {"username": session["user"]})["business_id"]}))

    if session["user"]:
        return render_template("profile.html", 
        username=username, business_id=business_id)

    return redirect(url_for("login"))


@app.route("/edit_info/<edit_business>", methods=["GET", "POST"])
def edit_info(edit_business):
    # retrieves categories of business from db
    categories = mongo.db.category.find().sort("name", 1)

    business_id = list(mongo.db.business.find_one(
        {"_id": ObjectId(edit_business)}))

    return render_template("edit_info.html", 
    categories=categories, business_id=business_id)


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("index"))



# Change debug to FALSE once app is complete
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")), debug=True)