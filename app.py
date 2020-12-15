import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
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
@app.route("/get_results")
def get_results():
    business = mongo.db.business.find()
    return render_template("index.html", results=business)


# Change debug to FALSE once app is complete
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")), debug=True)