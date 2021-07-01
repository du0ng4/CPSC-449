Andy Duong
aqduong@csu.fullerton.edu
Project 2: Microservice Implementation

To run the code, navigate to project directory in the terminal and run the following commands
    sh ./bin/init.sh
    foreman start

Sample commands to test each method are provided below


Available routes and methods along with sample tests:

Users Service:

method: users()
route: /users
desc: returns all users in database
sample test: http GET localhost:5000/users

method: followers(username)
desc: returns all followers given username
route: /users/<username>/follows
sample test: http GET localhost:5000/users/andy/follows

method: createUser()username, email, password)
desc: registers a new user account
route: /users
sample test: http POST localhost:5000/users username=buddy email=buddy@domain.com password=123

method: checkPassword(username, password)
desc: returns true if password matches stored password
route: /users/<username>
sample test: http POST localhost:5000/users/andy password=123

method: addFollower(username, usernameToFollow)
desc: starts following a new user
route: /users/<username>/follows
sample test: http POST localhost:5000/users/ryan/follows usernameToFollow=dang

method: removeFollower(username, usernameToRemove)
desc: stops following a user
route: /users/<username>/follows
sample test: http DELETE localhost:5000/users/andy/follows usernameToRemove=dang


Timelines Service:

method: getUserTimeline(username)
desc: returns recent posts from a user
route: /timelines/users/<username>
sample test: http GET localhost:5100/timelines/users/andy

method: getPublicTimeline()
desc: returns recent posts from all users
route: /timelines/public
sample test: http GET localhost:5100/timelines/public

method: getHomeTimeline(username)
desc: returns recent posts from all users that this user follows
route: /timelines/home
sample test: http GET localhost:5100/timelines/home username=andy following:='["ryan"]'

method: postTweet(username, text)
desc: posts a new tweet
route: /timelines
sample test: http POST localhost:5100/timelines username=andy text=wassup

