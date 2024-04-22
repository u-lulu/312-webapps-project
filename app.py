from flask_socketio import SocketIO, emit
import secrets
from flask import Flask, send_file, abort, make_response, request, jsonify, redirect, url_for, flash, \
    send_from_directory, render_template
import uuid
from uuid import uuid4
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from rolldice import roll_dice, DiceGroupException, DiceOperatorException
from func_timeout import func_timeout, FunctionTimedOut
import os
from pymongo import MongoClient
import bcrypt
from auth import hash_auth_token, is_authenticated, retrieve_user
import random


# Setting up the database
mongo_client = MongoClient("mongo")
db = mongo_client["animelovers"]
user_collection = db["user"]
message_collection = db["messages"]

app = Flask(__name__)
# Setting the upload folder to be in the uploads directory and only allowed certain file extensions
UPLOAD_FOLDER = 'uploads'
# PNG, JPEGS, AND GIFS
ALLOWED_EXTENSIONS = [b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', b'\xff\xd8\xff', 'GIF87a'.encode(), 'GIF89a'.encode()]
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# We limit uploads to 16 megabytes
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
# app.config['SECRET_KEY'] = '140472150481043457'
app.config['SECRET_KEY'] = secrets.token_hex(16)
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
    authenticated = is_authenticated(user_collection)
    username = ""
    profile_pic = None
    if authenticated:
        username = authenticated["user"]
        profile_pic = authenticated["Profile-Pic"]

    elif authenticated is False:
        username = "Guest"

    template = render_template('index.html', profile_pic=profile_pic, username=username, authenticated=authenticated)
    return serve_html(template)


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


# Function to check the file signature of a file
def check_file_signature(file):
    for file_signature in ALLOWED_EXTENSIONS:
        if file.startswith(file_signature):
            return True
    return False


@app.route("/upload-profile-pic", methods=["POST"])
def upload_file():
    authenticated_user = is_authenticated(user_collection)
    media_id = str(f'{random.randint(1, 10000000000000000)}') + "_"

    if "file" not in request.files:
        flash("No File part")
        return redirect_content()

    image_file = request.files["file"]

    # If a user didn't submit a file
    if image_file.filename == '':
        flash('No selected file')
        return redirect_content()

    # Authenticating the image
    file_signature = image_file.read(8)
    file_authenticated = check_file_signature(file_signature)
    image_file.seek(0)
    if file_authenticated:
        # Strip "/" from the filename and save it to the images directory
        filename = secure_filename(media_id + image_file.filename)
        image_file.save((os.path.join(app.config['UPLOAD_FOLDER'], filename)))
        # Store the image file_path in my database if the user is authenticated
        if authenticated_user:
            query = {"user": authenticated_user["user"]}
            update_query = {"$set": {"Profile-Pic": filename}}
            user_collection.update_one(query, update_query)
            message_collection.update_many({"username": authenticated_user["user"]}, {'$set': {"profile_pic": filename}})
        elif authenticated_user is False:
            flash("User isn't authenticated")
    else:
        flash("This file type isn't supported")

    return redirect_content()


# Route if a user wants to only see their profile pic
@app.route('/uploads/<filename>')
def serve_upload(filename):
    response = make_response(send_from_directory(app.config['UPLOAD_FOLDER'], filename))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


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
        user_collection.insert_one(
            {"user": username, "pass": hashedpassword, "Hashed authentication token": -1, "Profile-Pic": "./images/TEST_SniperDecoy.png"})
    return redirect_content()


# Javascript sends a post request to this endpoint to check if a user is authenticated
# (this is what makes the registration pages hide upon login) this isn't implemented
@app.route("/login", methods=["GET", "POST"])
def login():
    # Get username and password from the request data
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
            query = {"user": username, "Hashed authentication token": -1}
            update_query = {"$set": {"Hashed authentication token": hash_auth}}
            user_collection.update_one(query, update_query)

            # Create a response, send the auth token as a non session cookie, user will still be on the page due to AJAX
            response = make_response(redirect(url_for("homepage")))
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.set_cookie("Authentication-token", auth_token, expires=datetime.utcnow() + timedelta(hours=1),
                                httponly=True)
            return response
        else:
            # If authentication fails
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
        query = {"user": authenticated_user["user"], "pass": authenticated_user["pass"],
                 "Hashed authentication token": authenticated_user["Hashed authentication token"],
                 "Profile-Pic": authenticated_user["Profile-Pic"]}
        update_query = {"$set": {"Hashed authentication token": -1}}
        user_collection.update_one(query, update_query)

        # Invalidate the token and send a response via AJAX
        response = make_response(redirect(url_for("homepage")))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.set_cookie("Authentication-token", "", expires=0)
        return response


@socketio.on('chat_message')
def text_post(text):
    name = retrieve_user(user_collection)
    id = make_id()
    object = {
        "type": "text",
        "username": escape_html(name["user"]),
        "profile_pic": name["Profile-Pic"],
        "body": escape_html(text),
        "uuid": str(id)
    }

    emit('message', object)
    message_collection.insert_one(object)


@socketio.on('dice_message')
def dice_post(syntax):
    user = retrieve_user(user_collection)
    id = make_id()

    total, output = None, None
    try:
        total, output = func_timeout(5, roll_dice, args=[syntax])
    except DiceGroupException as e:
        return make_response(f"{e}", 400)
    except FunctionTimedOut as e:
        return make_response("It took too long to roll your dice (>5s). Roll less dice.", 400)
    except (ValueError, DiceOperatorException) as e:
        return make_response(
            "Could not properly parse your dice result. This usually means the result is much too large. Try rolling dice that will result in a smaller range of values.",
            400)

    object = {
        "type": "dice",
        "username": escape_html(user["user"]),
        "profile_pic": user["Profile-Pic"],
        "input": escape_html(syntax),
        "output": output,
        "total": total,
        "uuid": str(id)
    }

    emit('message', object)
    message_collection.insert_one(object)



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
    return jsonify(output), 200


@app.route("/posts/<id>", methods=['GET'])
def get_one_post(id):
    result = message_collection.find_one({"uuid": id})
    if result is None:
        return make_response("There are no messages with that ID.", 404)
    if '_id' in result:
        del result['_id']
    if 'id' in result:
        del result['id']
    return jsonify(result), 200


@socketio.on('connect')
def test_connect(auth):
    name = retrieve_user(user_collection)
    print(f"Client '{name['user']}' connected!")


@socketio.on('disconnect')
def test_connect():
    name = retrieve_user(user_collection)
    print(f"Client '{name['user']}' disconnected.")


if __name__ == "__main__":
    socketio.run(app, allow_unsafe_werkzeug=True)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
