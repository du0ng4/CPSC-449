Andy Duong
aqduong@csu.fullerton.edu
Project 6: Search Engine

This project is a DM microservice built with Python and using Redis as a data store

Dependencies:
    redis: sudo apt install --yes redis
    redis-py: python3 -m pip install redis
    nltk: python3 -m pip install nltk

Instructions to run microservice
    Have all dependencies installed locally on your computer (redis default port 6379)
    Open terminal at project directory
    run command: sh ./bin/init.sh   # WARNING: init.sh will flush redis databases
    run command: foreman start


Sample commands to test each method are provided below

Available routes and methods along with sample tests:

Users Service:
Note:   sample test commands meant to work with initialized data from init.sh
        sample test commands should be run in order before any other requests to api
        sample test commands also available at bottom for easy copy-paste

method: index(postId, text)
route: /index
desc: Adds the text of a post identified by postId to the inverted index
sample test: http post localhost:5000/index postId=4 text='hello this is a sample post'
expected return: {'Words Indexed': ['hello', 'sample', 'post']}

method: search(keyword)
route: /index
desc: Returns a list of postIds whose text contains keyword
sample test: http get localhost:5000/index keyword=hello
expected return: {'postIds': ['1', '2', '4']}

method: any(keywordList)
route: /index/any
desc: Returns a list of postIds whose text contains any of the words in keywordList
sample test: http get localhost:5000/index/any keywordList:='["hello", "cya"]'
expected return: {'postIds': ['1', '2', '3', '4']}

method: all(keywordList)
route: /index/all
desc: Returns a list of postIds whose text contains all of the words in keywordList
sample test: http get localhost:5000/index/all keywordList:='["hello", "bye"]'
expected return: {'postIds': ['1']}

method: exclude(includeList, excludeList)
route: /index/exclude
desc: Returns a list of postIds whose text contains any of the words in includeList unless they also contain a word in excludeList
sample test: http get localhost:5000/index/exclude includeList:='["hello"]' excludeList:='["bye"]'
expected return: {'postIds': ['2', '4']}

Sample Test Commands:

http post localhost:5000/index postId=4 text='hello this is a sample post'
http get localhost:5000/index keyword=hello
http get localhost:5000/index/any keywordList:='["hello", "cya"]'
http get localhost:5000/index/all keywordList:='["hello", "bye"]'
http get localhost:5000/index/exclude includeList:='["hello"]' excludeList:='["bye"]'
