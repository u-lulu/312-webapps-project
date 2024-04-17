from flask import Flask, send_file, abort, make_response, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, send, emit
from copy import deepcopy
import uuid
from uuid import uuid4
from datetime import datetime, timedelta
from html import escape
from rolldice import roll_dice, DiceGroupException, DiceOperatorException
from func_timeout import func_timeout, FunctionTimedOut
import os
from pymongo import MongoClient
import bcrypt
from auth import hash_auth_token, is_authenticated, retrieve_user
#python -m flask run


# Setting up the database
mongo_client = MongoClient("mongo:27017")
db = mongo_client["animelovers"]
user_collection = db["user"]
message_collection = db["messages"]

app = Flask(__name__)
app.config['SECRET_KEY'] = '140472150481043457'
socketio = SocketIO(app)


def escape_html(text):
    escaper_mapping = {
        "&": "&amp",
        "<": "&lt",
        ">": "&gt"
    }
    for key in escaper_mapping:
        text = text.replace(key, escaper_mapping[key])
    return text


def make_id():
    return str(uuid4())


def serve_file(path):
    response = make_response(send_file(path))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


def serve_html(file):
    response = make_response(file)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


def redirect_content():
    response = make_response(redirect(url_for("homepage")))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route("/")
def homepage():
    # Check if a user is authenticated and display their username
    authenticated_user = is_authenticated(user_collection)
    if authenticated_user:
        html_content = open("TEST_webpage.html", 'rb').read()
        updated_html_content = html_content.replace(b'{{Guest}}', authenticated_user["user"].encode())
        return serve_html(updated_html_content)

    elif authenticated_user is False:
        html_content = open("TEST_webpage.html", 'rb').read()
        updated_html_content = html_content.replace(b'{{Guest}}', "Guest".encode())
        return serve_html(updated_html_content)


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
    form = request.form
    username = form.getlist("username_reg")[0]
    password1 = form.getlist("password_reg")[0]
    password2 = form.getlist("password_reg2")[0]

    if password1 == password2:
        for user in user_collection.find():
            del user["_id"]
            if user["user"] == username:
                return redirect_content()
        hashedpassword = bcrypt.hashpw(password1.encode("utf-8"), bcrypt.gensalt())
        user_collection.insert_one({"user": username, "pass": hashedpassword, "Hashed authentication token": -1})

    return redirect_content()


@app.route("/login", methods=["GET", "POST"])
def login():
    form = request.form
    username = form.get("username_login")
    password = form.get("password_login")
    user = user_collection.find_one({'user': username}, {"_id": 0})
    if user:
        # Check if the stored hash matches the one in the database if it does send an auth token
        if bcrypt.checkpw(password.encode(), user["pass"]) is True:
            # Generate a token and update the database
            auth_token = str(uuid.uuid4())
            hash_auth = hash_auth_token(auth_token.encode())
            query = {"user":  username, "Hashed authentication token": -1}
            update_query = {"$set": {"Hashed authentication token": hash_auth}}
            user_collection.update_one(query, update_query)

            # Create a response, send the auth token as a non session cookie, and then redirect them to the home page
            response = make_response(redirect(url_for("homepage")))
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.set_cookie("Authentication-token", auth_token, expires=datetime.utcnow() + timedelta(hours=1), httponly=True)
            return response
        else:
            return redirect_content()
    else:
        return redirect_content()


@app.route("/logout", methods=["GET", "POST"])
def logout():
    authenticated_user = is_authenticated(user_collection)
    if authenticated_user is False:
        return redirect_content()
    elif authenticated_user is not False:
        # Update the database to revoke the token
        query = {"user": authenticated_user["user"], "pass": authenticated_user["pass"], "Hashed authentication token": authenticated_user["Hashed authentication token"]}
        update_query = {"$set": {"Hashed authentication token": -1}}
        user_collection.update_one(query, update_query)

        # Invalidate the token
        response = make_response(redirect(url_for("homepage")))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.set_cookie("Authentication-token", "", expires=0)
        return response


@app.route("/text-post", methods=['POST'])
def text_post():
    text = request.form.get('body_text').strip()
    name = retrieve_user(user_collection)  # TODO: Get name dynamically if the post is made with a login token
    id = make_id()
    object = {
        "type": "text",
        "username": escape_html(name),
        "body": escape_html(text),
        "uuid": id
    }
    message_collection.insert_one(object)
    return make_response(id, 201)


@app.route("/dice-post", methods=['POST'])
def dice_post():
    syntax = request.form.get('dice_text').strip()
    name = retrieve_user(user_collection)  # TODO: Get name dynamically if the post is made with a login token
    id = make_id()

    total, output = None, None
    try:
        total, output = func_timeout(5, roll_dice, args=[syntax])
    except DiceGroupException as e:
        return make_response(f"{e}", 400)
    except FunctionTimedOut as e:
        return make_response("It took too long to roll your dice (>5s). Roll less dice.", 400)
    except (ValueError, DiceOperatorException) as e:
        return make_response("Could not properly parse your dice result. This usually means the result is much too large. Try rolling dice that will result in a smaller range of values.",400)

    object = {
        "type": "text",
        "username": escape_html(name),
        "input": escape_html(syntax),
        "output": output,
        "total": total,
        "uuid": id
    }

    message_collection.insert_one(object)
    return make_response(id, 201)


@app.route("/posts", methods=['GET'])
def get_posts():
    all_posts = message_collection.find({})
    output = []
    for record in all_posts:
        if '_id' in record:
            del record['_id']
        if 'id' in record:
            del record['id']
        output.append(record)
    return make_response(jsonify(output), 200)


@app.route("/posts/<id>", methods=['GET'])
def get_one_post(id):
    result = message_collection.find_one({"uuid": id})
    if result is None:
        return make_response("There are no messages with that ID.", 404)
    if '_id' in result:
        del result['_id']
    if 'id' in result:
        del result['id']
    return make_response(jsonify(result), 200)


@socketio.on('connect')
def test_connect(auth):
    print("Client connected!")

@socketio.on('disconnect')
def test_connect():
    print("Client disconnected...")

if __name__ == "__main__":
    socketio.run(app)