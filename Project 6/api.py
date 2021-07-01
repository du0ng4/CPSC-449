# Andy Duong
# aqduong@csu.fullerton.edu
# Project 6: Search Engine

import sys
import textwrap
import logging.config

import bottle
from bottle import get, post, error, abort, request, response, HTTPResponse
import redis

import string
from datetime import datetime
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

# Set up app, redis, and logging

app = bottle.default_app()
app.config.load_config('./etc/api.ini')

r = redis.Redis(host='localhost', port=6379, db=0, encoding='utf-8', decode_responses=True)

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


# Routes

@get('/')
def home():
    return textwrap.dedent('''
        <h1>Project 6: Search Engine</h1>
        <p>By Andy Duong</p>\n
    ''')


@post('/index')
def index():
    userInput = request.json
    if not userInput:
        abort(400)
    posted_fields = userInput.keys()
    required_fields = {'postId', 'text'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields-posted_fields}')

    postId, text = userInput['postId'], userInput['text']

    text = text.lower()  # case-folding
    text = text.translate(str.maketrans('', '', string.punctuation))  # stripping punctuation
    text = text.split()  # splitting on whitespace
    text = list(set(text) - set(stopwords.words('english')))  # removing stopwords

    for word in text:
        if str(postId) not in r.lrange(word, 0, -1):
            r.lpush(word, postId)
         
    response.status = 201
    response.set_header('Content-Type', 'application/json')
    return {'Words Indexed': text }


@get('/index')
def search():
    userInput = request.json
    if not userInput:
        abort(400)
    posted_fields = userInput.keys()
    required_fields = {'keyword'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields-posted_fields}')
    keyword = userInput['keyword']

    postIds = r.lrange(keyword, 0, -1)
    postIds.sort()

    response.status = 200
    response.set_header('Content-Type', 'application/json')
    return {'postIds': postIds }


@get('/index/any')
def any():
    userInput = request.json
    if not userInput:
        abort(400)
    posted_fields = userInput.keys()
    required_fields = {'keywordList'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields-posted_fields}')
    keywordList = userInput['keywordList']
    if type(keywordList) is not list:
        abort(400, 'Argument must be of type list')
    
    r.delete('set1')
    for keyword in keywordList:
        temp = r.lrange(keyword, 0, -1)
        r.sadd('set1', *temp)

    postIds = list(r.smembers('set1'))
    postIds.sort()

    response.status = 200
    response.set_header('Content-Type', 'application/json')
    return {'postIds': postIds}


@get('/index/all')
def all():
    userInput = request.json
    if not userInput:
        abort(400)
    posted_fields = userInput.keys()
    required_fields = {'keywordList'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields-posted_fields}')
    keywordList = userInput['keywordList']
    if type(keywordList) is not list:
        abort(400, 'Argument must be of type list')

    r.delete('set1')
    temp = r.lrange(keywordList[0], 0, -1)
    r.sadd('set1', *temp)
    for word in keywordList[1:]:
        temp = r.lrange(word, 0, -1)
        r.delete('set2')
        r.sadd('set2', *temp)
        temp =  r.sinter('set1', 'set2')
        r.delete('set1')
        r.sadd('set1', *temp)

    postIds = list(r.smembers('set1'))
    postIds.sort()

    response.status = 200
    response.set_header('Content-Type', 'application/json')
    return {'postIds': postIds}


@get('/index/exclude')
def exclude():
    userInput = request.json
    if not userInput:
        abort(400)
    posted_fields = userInput.keys()
    required_fields = {'includeList', 'excludeList'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields-posted_fields}')
    includeList, excludeList = userInput['includeList'], userInput['excludeList']
    if type(includeList) is not list or type(excludeList) is not list:
        abort(400, 'Arguements must be of type list')

    r.delete('set1')
    for keyword in includeList:
        temp = r.lrange(keyword, 0, -1)
        r.sadd('set1', *temp)

    r.delete('set2')
    for keyword in excludeList:
        temp = r.lrange(keyword, 0, -1)
        r.sadd('set2', *temp)

    postIds =  list(r.sdiff('set1', 'set2'))
    postIds.sort()

    response.status = 200
    response.set_header('Content-Type', 'application/json')
    return {'postIds': postIds}

    