# Andy Duong
# aqduong@csu.fullerton.edu
# Project 5: NoSQL

import sys
import textwrap
import logging.config

import bottle
from bottle import get, post, error, abort, request, response, HTTPResponse
import boto3
from boto3.dynamodb.conditions import Key, Attr

from datetime import datetime

# Set up app, db, and logging

app = bottle.default_app()
app.config.load_config('./etc/api.ini')

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
table = dynamodb.Table('directmessages')

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
        <h1>Project 5: NoSQL</h1>
        <p>By Andy Duong</p>\n
    ''')

@post('/messages')
def sendDirectMessage():
    userInput = request.json
    if not userInput:
        abort(400)
    posted_fields = userInput.keys()
    required_fields = {'to', 'from', 'message'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields-posted_fields}')

    directMessage = {
        'messageId': table.item_count + 1,
        'timestamp': datetime.now().isoformat(),
        'to': userInput['to'],
        'from': userInput['from'],
        'message': userInput['message']
    }

    if 'quickReplies' in userInput:
        directMessage['quickReplies'] = userInput['quickReplies']

    table.put_item(Item=directMessage)

    response.status = 201
    return directMessage


@post('/messages/<messageId>')
def replyToDirectMessage(messageId):
    messageId = int(messageId)
    userInput = request.json
    if not userInput:
        abort(400)
    posted_fields = userInput.keys()
    required_fields = {'message'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields-posted_fields}')

    originalMessage = table.query(KeyConditionExpression=Key('messageId').eq(messageId))['Items'][0]
    
    if type(userInput['message']) is int:
        if "quickReplies" not in originalMessage:
            abort(400, 'quick-reply number to DM without quick-replies field')
        else:
            if userInput['message'] < 0 or userInput['message'] >= len(originalMessage['quickReplies']):
                abort(400, 'invalid quick-reply number')

    directMessage = {
        'messageId': table.item_count + 1,
        'timestamp': datetime.now().isoformat(),
        'to': originalMessage['to'],
        'from': originalMessage['from'],
        'message': userInput['message'],
        'in-reply-to': messageId
    }

    table.put_item(Item=directMessage)

    response.status = 201
    return directMessage


@get('/messages')
def listDirectMessagesFor():
    userInput = request.json
    if not userInput:
        abort(400)
    posted_fields = userInput.keys()
    required_fields = {'username'}
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields-posted_fields}')

    response = table.query(
        IndexName = 'to-index',
        KeyConditionExpression=Key('to').eq(userInput['username'])
    )
    items = response['Items']
    if not items:
        abort(404)

    return {'directmessages': items}


@get('/messages/<messageId>')
def listRepliesTo(messageId):
    response = table.query(
        IndexName = 'in-reply-to-index',
        KeyConditionExpression=Key('in-reply-to').eq(int(messageId))
    )
    items = response['Items']
    if not items:
        abort(404)

    return {'directmessages': items}
