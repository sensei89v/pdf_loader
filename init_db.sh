#!/bin/bash

echo "CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login VARCHAR(128) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL
); " | sqlite3 $1

echo "CREATE TABLE pdf (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename VARCHAR(1024) NOT NULL,
    pdf BLOB NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT NOW,
    FOREIGN KEY(user_id) REFERENCES user(id)
); " | sqlite3 $1

echo "CREATE TABLE page (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pdf_id INTEGER NOT NULL,
    page_num INTEGER NOT NULL,
    page BLOB NOT NULL,
    FOREIGN KEY(pdf_id) REFERENCES pdf(id)
);" | sqlite3 $1

