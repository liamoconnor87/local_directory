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
    local_business = list(mongo.db.business.find())
    return render_template("index.html", results=local_business)


@app.route("/search", methods=["GET", "POST"])
def search():
    query_one = request.form.get("query-1")
    query_two = request.form.get("query-2")
    query = str(query_one + " " + query_two)
    business = list(mongo.db.business.find({"$text": {"$search": query}}))
    return render_template("results.html", results=business, query=query)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Retrieves categories of business from db
    categories = mongo.db.category.find().sort("category_name", 1)

    if request.method == "POST":
        # Checks if username already exists in the db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # Checks if email already exists in the db
        existing_email = mongo.db.business.find_one(
            {"email": request.form.get("email").lower()})

        # Verify email matches
        email_one = request.form.get("email")
        email_two = request.form.get("email2")

        # Verify password matches
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

        category_id = mongo.db.category.find_one(
            {"category_name": request.form.get("category_name")})

        register_business = {
            "name": request.form.get("business_name"),
            "website": request.form.get("website").lower(),
            "email": request.form.get("email").lower(),
            "address": request.form.get("address"),
            "category_name": category_id["category_name"],
            "category_id": category_id["_id"]
        }

        mongo.db.business.insert_one(register_business)

        register_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "business_id": register_business["_id"]
        }

        mongo.db.users.insert_one(register_user)

        # Puts the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html", categories=categories)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Checks if username exists in the db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Checks is password matches db
            if check_password_hash(
               existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))

                    if str(session["user"]) == "admin":
                        return redirect(url_for("admin_page",
                                        admin_user=session["user"]))

                    else:
                        return redirect(url_for("profile",
                                        username=session["user"]))

            else:
                # If password does not match
                flash("Incorrect Username/Password")
                return redirect(url_for("login"))

        else:
            # If username does not match
            flash("Incorrect Username/Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/admin_page/<admin_user>", methods=["GET", "POST"])
def admin_page(admin_user):

    if str(session["user"]) == "admin":

        admin_name = mongo.db.users.find_one(
            {"username": session["user"]})["username"]

        if request.method == "POST":
            exisitng_category = mongo.db.category.find_one(
                {"category_name": request.form.get("business-type").lower()})

            if exisitng_category:
                flash("Category already exists")
                return redirect(url_for("admin_page",
                                admin_user=session["user"]))

            add_category = {
                "category_name": request.form.get("business-type")
            }
            mongo.db.category.insert_one(add_category)
            flash("Category added")
            return redirect(url_for("admin_page", admin_user=session["user"]))

        return render_template("admin_page.html", username=admin_name)

    return redirect(url_for("index"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Retrieves session user's username from the db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    business_id = list(mongo.db.business.find({"_id": mongo.db.users.find_one(
        {"username": session["user"]})["business_id"]}))

    if session["user"]:
        return render_template(
            "profile.html", username=username, business_id=business_id)

    return redirect(url_for("index"))


@app.route("/edit_info/<edit_business>", methods=["GET", "POST"])
def edit_info(edit_business):
    # Retrieves categories of business from db
    categories = mongo.db.category.find().sort("category_name", 1)

    if request.method == "POST":

        # Checks if email already exists in the db
        existing_email = mongo.db.business.find_one(
            {"email": request.form.get("email").lower()})

        current_email = mongo.db.business.find_one(
            {"_id": ObjectId(edit_business)})["email"]

        email_input = request.form.get("email").lower()

        # Verify email matches
        email_one = request.form.get("email")
        email_two = request.form.get("email2")

        if email_one != email_two:
            flash("Emails must match to verify")
            return redirect(url_for("edit_info", edit_business=edit_business))

        elif current_email != email_input:
            if existing_email:
                flash("Email is already exists")
                return redirect(url_for("edit_info",
                                edit_business=edit_business))

        # Retrieves current category id from business to remove it
        current_category_id = mongo.db.business.find_one(
            {"_id": ObjectId(edit_business)})

        current_category_id.pop("category_id")

        category_id = mongo.db.category.find_one(
            {"category_name": request.form.get("category_name")})

        update_business = {
            "name": request.form.get("business_name"),
            "website": request.form.get("website").lower(),
            "email": request.form.get("email").lower(),
            "address": request.form.get("address"),
            "category_name": category_id["category_name"],
            "category_id": category_id["_id"]
        }

        mongo.db.business.update(
            {"_id": ObjectId(edit_business)}, update_business)

        flash("Business Information was updated!")
        return redirect(url_for("profile", username=session["user"]))

    business_id = mongo.db.business.find_one(
        {"_id": ObjectId(edit_business)})

    user_business = mongo.db.users.find_one(
        {"username": session["user"]})["business_id"]

    if session["user"]:
        if str(edit_business) == str(user_business):
            return render_template(
                "edit_info.html",
                categories=categories, business_id=business_id)

    return redirect(url_for("index"))


@app.route("/delete_probus/<delete_business>")
def delete_probus(delete_business):
    # Retrieves users ObjectID
    user_id = mongo.db.users.find_one(
        {"username": session["user"]})["_id"]

    if session["user"]:
        flash("Your Profile and Business have been removed from our database")
        session.pop("user")
        mongo.db.business.remove({"_id": ObjectId(delete_business)})
        mongo.db.users.remove({"_id": ObjectId(user_id)})

        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    # Remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("index"))


# Change debug to FALSE for debugging
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")), debug=False)
