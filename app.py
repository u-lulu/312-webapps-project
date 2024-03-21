from flask import Flask, send_file, abort, make_response
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


@app.route("/text-post", methods=['POST'])
def text_post():
    text = request.form.get('body_text').strip()
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
    syntax = request.form.get('dice_text').strip()
    name = "Guest" # TODO: Get name dynamically if the post is made with a login token
    id = make_id()

    total,output = None,None
    try:
        total,output = func_timeout(5, roll_dice,args=[syntax])
    except DiceGroupException as e:
        return make_response(f"{e}",400)
    except FunctionTimedOut as e:
        return make_response("It took too long to roll your dice (>5s). Roll less dice.",400)
    except (ValueError, DiceOperatorException) as e:
        return make_response("Could not properly parse your dice result. This usually means the result is much too large. Try rolling dice that will result in a smaller range of values.",400)

    object = {
        "type":"text",
        "username":escape_html(name),
        "input":escape_html(syntax),
        "output":output,
        "total":total,
        "uuid":id
    }

    message_collection.insert_one(object)
    return make_response(id,201)

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