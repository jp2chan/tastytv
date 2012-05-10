from __future__ import with_statement
from flask import Flask, url_for, request, render_template, g, json
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing

# python server.py
# Super hacky lightweight server which outputs data

DATABASE = 'tasty.db'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    """Returns a new connection to the database."""
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    """Make sure we are connected to the database
    """
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

@app.route("/hello")
def hello():
    return "Hello World!"

@app.route("/")
def index():
    showString = '''select tvshows.* from tvshows LIMIT 5'''
    showsToQueue = query_db(showString)
    jsShows = json.dumps(showsToQueue)
    return render_template('index.html', jsShows=jsShows)

@app.route("/friends")
def friends():
    friends=query_db('''select friends.* from friends''')
    return render_template('friends.html', friends=friends)

@app.route("/feeling")
def feeling():
    genres=query_db('''select genres.* from genres ''')
    return render_template('feeling.html',genres = genres)

@app.route("/browse")
def browse():
    shows=query_db('''select tvshows.* from tvshows ''')
    return render_template('browse.html',shows=shows)

@app.route("/watchbox")
def watchbox():
    return render_template('watchbox.html')

@app.route("/watch")
def watch():
    return render_template('watch.html')

# after you've selected friends to watch with
@app.route("/watch/<friends>")
def watch(friends=None):
    friendArray = friends.split("|")[:-1]
    showID = friendArray.pop()
    showID = "'"+showID+"'"
    friendArray = ','.join(friendArray)
    friendArray = '('+friendArray+')'
    sqlString = '''select friends.* from friends where user_id in '''+friendArray
    friendInfo = query_db(sqlString)
    watchbox = query_db('''select tvshows.* from tvshows,watchbox where watchbox.user_id=0 and watchbox.show_id = tvshows.show_id''')
    showString = '''select tvshows.* from tvshows where tvshows.show_id='''+showID
    showToQueue = query_db(showString)
    return render_template('watch.html',friends=friendInfo,watchbox=watchbox,shows=showToQueue, json_struct=json.dumps(showToQueue[0]))

# after you've selected friends to watch with, show you three shows
@app.route("/chooseShow/<friends>")
def chooseShow(friends=None):
    friendArray = friends.split("|")[:-1]
    friendArray = ','.join(friendArray)
    friendArray = '('+friendArray+')'
    sqlString = '''select friends.* from friends where user_id in '''+friendArray
    friendInfo = query_db(sqlString)
    videos = query_db('''select tvshows.* from tvshows,watchbox where watchbox.user_id=0 and watchbox.show_id = tvshows.show_id limit 3''') 
    return render_template('chooseShow.html',friends=friendInfo,videos=videos)


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')
    
if __name__ == "__main__":
    app.run(debug=True)
