from flask import Flask, send_file, abort, make_response, request 
import os
from pymongo import MongoClient
import bcrypt
#python -m flask run

app = Flask(__name__)
mongo_client = MongoClient("mongo:27017")
db = mongo_client["animelovers"]
user_collection = db["users"]

def serve_file(path):
    response = make_response(send_file(path))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route("/")
def homepage():
    return serve_file("TEST_webpage.html")

@app.route("/styles.css")
def css():
    return serve_file("styles.css")

@app.route("/scripts/<name>.js")
def get_js(name):
    if os.path.exists("scripts/" + name + ".js"):
        return serve_file("scripts/" + name + ".js")
    else:
        return abort(404)

@app.route("/favicon.ico")
def favicon():
    return serve_file("favicon.ico")

@app.route("/images/<filename>")
def get_image(filename):
    if os.path.exists("images/" + filename):
        return serve_file("images/" + filename)
    else:
        return abort(404)

@app.route("/register", methods=["GET", "POST"])
def register():
    form=request.form
    username=form.getlist("username_reg")[0]
    password1=form.getlist("password_reg")[0]
    password2=form.getlist("password_reg2")[0]

    if password1==password2:
        for user in user_collection.find():
            del user["_id"]
            if user["user"]==username:
                return serve_file("TEST_webpage.html")
        hashedpassword=bcrypt.hashpw(password1.encode("utf-8"),bcrypt.gensalt())
        user_collection.insert_one({"user":username, "pass":hashedpassword, "Hashed authentication token":-1})

    return serve_file("TEST_webpage.html")
