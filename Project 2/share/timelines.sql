-- $ sqlite3 timelines.db < timelines.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS timelines;
CREATE TABLE posts (
    username VARCHAR,
    text VARCHAR,
    timestamp VARCHAR
);
INSERT INTO posts(username, text, timestamp) VALUES('andy', 'hello', '2021-03-12 02:24:10.611045');
INSERT INTO posts(username, text, timestamp) VALUES('ryan', 'bye bye', '2021-03-13 02:24:10.611045');
COMMIT;