Andy Duong
aqduong@csu.fullerton.edu
Project 5: NoSQL

This project is a DM microservice built with Python and DynamoDB Local

Instructions to run microservice
    Have DynamoDB deployed locally on your computer (default port 8000)
    Open project directory
    run command: python3 ./bin/schema.py
    run command: foreman start
If python script schema.py tells you to run it again, please run it again


Sample commands to test each method are provided below

Available routes and methods along with sample tests:

Users Service:
Note:   sample test commands should be run in order before any other requests to api
        sample test commands also available at bottom for easy copy-paste

method: sendDirectMessage(to, from, message, quickReplies=None)
route: /messages
desc: Sends a DM to a user, quickReplies may or may not be included
sample test: http post localhost:5000/messages to='Andy' from='Ryan' message='reply faster' quickReplies:='["okay", "no"]'

method: replyToDirectMessage(messageId, message)
route: /messages/<messageId>
desc: Replies to a DM; if replying to a DM with a quick-reply field, an integer may be included in the message field
sample test: http post localhost:5000/messages/4 message:=1

method: listDirectMessagesFor(username)
route: /messages
desc: list the DMs a user has received
sample test: http get localhost:5000/messages username=Andy

method: listRepliesTo(messageId)
route /messages/<messageId>
desc: lists the replies sent to a DM
sample test: http get localhost:5000/messages/2


Sample Test Commands:

http post localhost:5000/messages to='Andy' from='Ryan' message='reply faster' quickReplies:='["okay", "no"]'
http post localhost:5000/messages/4 message:=1
http get localhost:5000/messages username=Andy
http get localhost:5000/messages/2
