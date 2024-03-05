from flask import Flask, send_file, abort
import os
#python -m flask run

app = Flask(__name__)

@app.route("/")
def homepage():
    return send_file("TEST_webpage.html")

@app.route("/favicon.ico")
def favicon():
    return send_file("favicon.ico")

@app.route("/images/<filename>")
def get_image(filename):
    if os.path.exists("images/" + filename):
        return send_file("images/" + filename)
    else:
        return abort(404)