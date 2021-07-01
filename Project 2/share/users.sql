-- $ sqlite3 users.db < users.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    username VARCHAR primary key,
    email VARCHAR,
    password VARCHAR,
    UNIQUE(username, email)
);
CREATE TABLE follows (
    username VARCHAR,
    following VARCHAR,
    CONSTRAINT username_following PRIMARY KEY(username, following)
);
INSERT INTO users(username, email, password) VALUES('andy','andy@domain.com','123');
INSERT INTO users(username, email, password) VALUES('ryan','ryan@domain.com','456');
INSERT INTO users(username, email, password) VALUES('dang','dang@domain.com','789');
INSERT INTO follows(username, following) VALUES('andy', 'ryan');
INSERT INTO follows(username, following) VALUES('andy', 'dang');
INSERT INTO follows(username, following) VALUES('ryan', 'andy');
INSERT INTO follows(username, following) VALUES('dang', 'ryan');
COMMIT;