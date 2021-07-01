# Andy Duong
# aqduong@csu.fullerton.edu
# Project 5: NoSQL


import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

try:
    table = dynamodb.create_table(
        TableName='directmessages',
        KeySchema=[
            {
                'AttributeName': 'messageId',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'messageId',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'to',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'in-reply-to',
                'AttributeType': 'N'
            }
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'to-index',
                'KeySchema': [
                    {
                        'AttributeName': 'to',
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
            {
                'IndexName': 'in-reply-to-index',
                'KeySchema': [
                    {
                        'AttributeName': 'in-reply-to',
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    table.meta.client.get_waiter('table_exists').wait(TableName='directmessages')

    table.put_item(
        Item={
            'messageId': 1,
            'timestamp': datetime.now().isoformat(),
            'to': 'Andy',
            'from': 'Ryan',
            'message': 'hello'
        }
    )
    table.put_item(
        Item={
            'messageId': 2,
            'timestamp': datetime.now().isoformat(),
            'to': 'Andy',
            'from': 'Ryan',
            'message': 'Are you ignoring me?',
            'quickReplies': ['yes', 'no']
        }
    )
    table.put_item(
        Item={
            'messageId': 3,
            'timestamp': datetime.now().isoformat(),
            'to': 'Ryan',
            'from': 'Andy',
            'message': 1,
            'in-reply-to': 2
        }
    )
    print('Script ran successfully')

except:
    table = dynamodb.Table('directmessages')
    table.delete()
    print('Please re-run script')
