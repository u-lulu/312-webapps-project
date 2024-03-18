from flask import Flask, send_file, abort, make_response, request, jsonify
from pymongo import MongoClient
from copy import deepcopy
from uuid import uuid4
import os
#python -m flask run

mongo_client = MongoClient("mongo:27017")
db = mongo_client["animelovers"]
message_collection = db["messages"]

app = Flask(__name__)

def escape_html(text):
    escaper_mapping = {
        "&":"&amp",
        "<":"&lt",
        ">":"&gt"
    }
    for key in escaper_mapping:
        text = text.replace(key, escaper_mapping[key])
    return text

def make_id():
    return str(uuid4())

def serve_file(path):
    response = make_response(send_file(path),200)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route("/", methods=['GET'])
def homepage():
    return serve_file("TEST_webpage.html")

@app.route("/styles.css", methods=['GET'])
def css():
    return serve_file("styles.css")

@app.route("/scripts/<name>.js", methods=['GET'])
def get_js(name):
    if os.path.exists("scripts/" + name + ".js"):
        return serve_file("scripts/" + name + ".js")
    else:
        return abort(404)

@app.route("/favicon.ico", methods=['GET'])
def favicon():
    return serve_file("favicon.ico")

@app.route("/images/<filename>", methods=['GET'])
def get_image(filename):
    if os.path.exists("images/" + filename):
        return serve_file("images/" + filename)
    else:
        return abort(404)

@app.route("/text-post", methods=['POST'])
def text_post():
    text = request.form.get('body_text')
    name = "Guest" # TODO: Get name dynamically if the post is made with a login token
    id = make_id()
    object = {
        "type":"text",
        "username":escape_html(name),
        "body":escape_html(text),
        "uuid":id
    }
    message_collection.insert_one(object)
    return make_response(id,201)

@app.route("/dice-post", methods=['POST'])
def dice_post():
    pass

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
    return make_response(jsonify(output),200)

@app.route("/posts/<id>", methods=['GET'])
def get_one_post(id):
    result = message_collection.find_one({"uuid":id})
    if result is None:
        return make_response("There are no messages with that ID.",404)
    if '_id' in result:
        del result['_id']
    if 'id' in result:
        del result['id']
    return make_response(jsonify(result),200)