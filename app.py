from flask import Flask, request, render_template, make_response, send_file
from datetime import datetime
from pymongo import MongoClient
import io
import base64
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient(
    "mongodb+srv://bjab:Emiafreabe69@cluster0.1pmw0.mongodb.net/track?retryWrites=true&w=majority"
)

app.db = client.trackDB
Track = app.db["track"]

Track.insert({'userId': 0})


def getNextUserId():
    currentId = Track.find({})[0]['userId']
    nextId = currentId + 1
    Track.update({}, {"$set": {"userId": nextId}})
    return nextId


@app.route("/")
def home():
    print("Home")
    return render_template("home.html")


@app.route("/contact/")
def contact():
    return render_template("contact.html")


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route('/static/pixel.gif')
def returnPixel():
    gif = 'R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
    gif_str = base64.b64decode(gif)

    if (request.cookies.get('userid')):
        userid = request.cookies.get('userid')
    else:
        userid = getNextUserId()

    now = datetime.utcnow()
    print(now, request.args.get('page'), userid)

    response = make_response(
        send_file(io.BytesIO(gif_str), mimetype='image/gif'), 200)
    response.set_cookie('userid', str(userid), max_age=1296000)
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0')
