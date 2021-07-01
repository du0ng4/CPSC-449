#!/bin/sh

echo "Flushing all databases"
redis-cli FLUSHALL

echo "Initializing test data"
redis-cli LPUSH hello 1 
redis-cli LPUSH hello 2
redis-cli LPUSH bye 1
redis-cli LPUSH cya 3
echo "Success"
