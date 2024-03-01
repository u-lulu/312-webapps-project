from flask import Flask
#flask --app host run

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"