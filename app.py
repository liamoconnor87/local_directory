import os
from flask import Flask
if os.path.exists("env.py"):
    import env
# pip3 install Flask


# Creating an instance of flask
app = Flask(__name__)


@app.route("/")
def hello():
    return "Local Directory test!"


# Change debug to FALSE once app is complete
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")), debug=True)