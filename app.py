from flask import Flask, request, render_template, make_response, send_file
from datetime import datetime
from pymongo import MongoClient
import io
import base64
from tabulate import tabulate

app = Flask(__name__)

client = MongoClient(
    "mongodb+srv://xxx:yyy@cluster0.1pmw0.mongodb.net/track?retryWrites=true&w=majority"
)

app.db = client.trackDB
trackdb = app.db["track"]
userdb = app.db["user"]

try:
    currentId = userdb.find({})[0]['userid']
except (IndexError, KeyError):
    userdb.insert({'userid': 0})


def get_next_userid():
    currentid = userdb.find({})[0]['userid']
    nextid = currentid + 1
    userdb.update({}, {"$set": {"userId": nextid}})
    return nextid


def count_views(seq, pred):
    return sum(1 for v in seq if pred(v))


def count_visitors(tracks, page):
    visitors = set()
    for track in tracks:
        if (track.get('url') == page):
            visitors.add(track.get('userid'))
    return len(visitors)


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


@app.route("/report/")
def report():

    args = request.args

    start = datetime.strptime(
        args.get('date') + " " + args.get('start'), "%Y-%m-%d %H:%M:%S")

    end = datetime.strptime(
        args.get('date') + " " + args.get('end'), "%Y-%m-%d %H:%M:%S")

    tracks = list(trackdb.find({'time': {'$gt': start, '$lt': end}}))

    # get unique pages
    track_pages = set()
    for track in tracks:
        track_pages.add(track.get('url'))

    headers = ["url", "page views", "visitors"]
    rows = []
    for page in track_pages:
        rows.append([
            page,
            str(count_views(tracks, lambda p: p.get('url') == page)),
            count_visitors(tracks, page)
        ])

    return tabulate(rows, headers)


@app.route('/static/pixel.gif')
def returnpixel():
    gif = 'R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
    gif_str = base64.b64decode(gif)

    if (request.cookies.get('userid')):
        userid = request.cookies.get('userid')
    else:
        userid = get_next_userid()

    now = datetime.utcnow()

    print(now, request.args.get('page'), userid)

    trackdb.insert_one({
        'time': now,
        'url': request.args.get('page'),
        'userid': userid
    })

    response = make_response(
        send_file(io.BytesIO(gif_str), mimetype='image/gif'), 200)
    response.set_cookie('userid', str(userid), max_age=1296000)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0')
