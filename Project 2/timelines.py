# Andy Duong
# aqduong@csu.fullerton.edu
# Project 2: Microservice Implementation

import sys
import textwrap
import logging.config
import sqlite3

import bottle
from bottle import get, post, error, abort, request, response, HTTPResponse
from bottle.ext import sqlite

import time
import string
from datetime import datetime

# Set up app, sqlite, and logging

app = bottle.default_app()
app.config.load_config('./etc/api.ini')

plugin = sqlite.Plugin(app.config['sqlite.timelines'])
app.install(plugin)

logging.config.fileConfig(app.config['logging.config'])

# Return errors in JSON
# Adapted from <https://stackoverflow.com/a/39818780>

def json_error_handler(res):
    if res.content_type == 'application/json':
        return res.body
    res.content_type = 'application/json'
    if res.body == 'Unknown Error.':
        res.body = bottle.HTTP_CODES[res.status_code]
    return bottle.json_dumps({'error': res.body})


app.default_error_handler = json_error_handler

# Disable warnings produced by Bottle 0.12.19.
#
#  1. Deprecation warnings for bottle_sqlite
#  2. Resource warnings when reloader=True
#
# See
#  <https://docs.python.org/3/library/warnings.html#overriding-the-default-filter>
#
if not sys.warnoptions:
    import warnings
    for warning in [DeprecationWarning, ResourceWarning]:
        warnings.simplefilter('ignore', warning)

# Simplify DB access
#
# Adapted from
# <https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#easy-querying>
def query(db, sql, args=(), one=False):
    cur = db.execute(sql, args)
    rv = [dict((cur.description[idx][0], value)
          for idx, value in enumerate(row))
          for row in cur.fetchall()]
    cur.close()

    return (rv[0] if rv else None) if one else rv

def execute(db, sql, args=()):
    cur = db.execute(sql, args)
    id = cur.lastrowid
    cur.close()
    return id

# Routes

@get('/')
def home():
    return textwrap.dedent('''
        <h1>Timelines Service for Project 2</h1>
        <p>By Andy Duong</p>\n
    ''')

# route for method getUserTimeline(username)
@get('/timelines/users/<username>')
def getUserTimeline(username, db):
    sql = 'SELECT * FROM posts WHERE username = ? ORDER BY timestamp DESC LIMIT 25'
    timeline = query(db, sql, [username], one=False)
    if not timeline:
        abort(404)
    return {'timeline': timeline}

# route for method getPublicTimeline()
@get('/timelines/public')
def getPublicTimeline(db):
    sql = 'SELECT * FROM posts ORDER BY timestamp DESC LIMIT 25'
    timeline = query(db, sql, one=False)
    if not timeline:
        abort(404)
    return {'timeline': timeline}

# route for method getHomeTimeline(username)
@get('/timelines/home')
def getHomeTimeline(db):
    user = request.json
    if not user:
        abort(400)
    posted_fields = user.keys()
    required_fields = {'username', 'following'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')
    
    users_followed = user['following']

    sql = 'SELECT * FROM posts WHERE '
    for user in users_followed:
        sql += "username = '" + str(user) + "' OR "
    sql = sql[:-4]
    sql+= ' ORDER BY timestamp DESC LIMIT 25'

    print(sql)
    timeline = query(db, sql, one=False)
    if not timeline:
        abort(404)
    return {'timeline': timeline}

# route for method postTweet(username, text)
@post('/timelines')
def postTweet(db):
    userInput = request.json
    if not userInput:
        abort(400)

    posted_fields = userInput.keys()
    required_fields = {'username', 'text'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')
    
    timestamp = str(datetime.now())
    post = {}
    post['timestamp'] = timestamp
    post['username'] = userInput['username']
    post['text'] = userInput['text']

    try:
        post['id'] = execute(db, '''
            INSERT INTO posts(username, text, timestamp)
            VALUES(:username, :text, :timestamp)
            ''', post)
    except sqlite3.IntegrityError as e:
        abort(409, str(e))

    response.status = 201
    return post

