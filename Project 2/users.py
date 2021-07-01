# Andy Duong
# aqduong@csu.fullerton.edu
# Project 2: Microservice Implementation
#

import sys
import textwrap
import logging.config
import sqlite3

import bottle
from bottle import get, post, delete, error, abort, request, response, HTTPResponse
from bottle.ext import sqlite

# Set up app, plugins, and logging
#
app = bottle.default_app()
app.config.load_config('./etc/api.ini')

plugin = sqlite.Plugin(app.config['sqlite.users'])
app.install(plugin)

logging.config.fileConfig(app.config['logging.config'])


# Return errors in JSON
#
# Adapted from <https://stackoverflow.com/a/39818780>
#
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
#
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
        <h1>Users Service for Project 2</h1>
        <p>By Andy Duong</p>
    ''')

# route for method createUser(username, email, password)
@post('/users')
def create_user(db):
    user = request.json
    if not user:
        abort(400)

    required_fields = {'username', 'email', 'password'}
    posted_fields = user.keys()

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    try:
        user['id'] = execute(db, '''
            INSERT INTO users(username, email, password)
            VALUES(:username, :email, :password)
            ''', user)
    except sqlite3.IntegrityError as e:
        abort(409, str(e))

    response.status = 201
    response.set_header('Location', f"/users/{user['id']}")
    return 'True'

# route for method to return all users
@get('/users')
def users(db):
    all_users = query(db, 'SELECT * FROM users;')
    return {'users': all_users}

# route for method checkPassword(username, password)
@post('/users/<username>')
def check_password(username, db):
    input_password = request.json
    if not input_password:
        abort(400)

    posted_fields = input_password.keys()
    required_fields = {'password'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')
    
    password = query(db, 'SELECT password FROM users WHERE username = ?', [username], one=True)
    if not password:
        abort(404)

    if password['password'] == input_password['password']:
        response.status = 200
        return 'True'
    else:
        response.status = 401
        return 'False'
        
# route for method addFollower(username, usernameToFollow)
@post('/users/<username>/follows')
def add_follower(username, db):
    follow = request.json
    if not follow:
        abort(400)

    posted_fields = follow.keys()
    required_fields = {'usernameToFollow'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    usernameToFollow = query(db, 'SELECT * FROM users WHERE username = ?', [follow['usernameToFollow']], one=True)
    if not usernameToFollow:
        abort(404)

    follow['username'] = username

    try:
        follow['id'] = execute(db, '''
            INSERT INTO follows(username, following)
            VALUES(:username, :usernameToFollow)
            ''', follow)
    except sqlite3.IntegrityError as e:
        abort(409, str(e))

    response.status = 201
    return 'True'

# route for method removeFollower(username, usernameToRemove)
@delete('/users/<username>/follows')
def remove_follower(username, db):
    follow = request.json
    if not follow:
        abort(400)

    posted_fields = follow.keys()
    required_fields = {'usernameToRemove'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    usernameToRemove = query(db, 'SELECT * FROM users WHERE username = ?', [follow['usernameToRemove']], one=True)
    if not usernameToRemove:
        abort(404)

    follow['username'] = username

    try:
        follow['id'] = execute(db, '''
            DELETE FROM follows
            WHERE following = :usernameToRemove AND username = :username
            ''', follow)
    except sqlite3.IntegrityError as e:
        abort(409, str(e))

    response.status = 200
    return 'True'
    
# route for method to return all follows from all users
@get('/users/<username>/follows')
def followers(username, db):
    all_follows = query(db, 'SELECT * FROM follows WHERE username = ?', [username])
    return {'follows': all_follows}
