from flask import Flask, send_file, abort, make_response, request 
import os
#python -m flask run

app = Flask(__name__)

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
    print(form.getlist("username_reg")[0])
    return serve_file("TEST_webpage.html")
