import os
import sqlite3
from flask import Flask, jsonify as flask_jsonify, g

from config import DATABASE, CREATE_DB


def jsonify(*args, **kwargs):
    response = flask_jsonify(*args, **kwargs)
    if not response.data.endswith(b'\n'):
        response.data += b'\n'
    return response


app = Flask(__name__)
app.debug = bool(os.environ.get('DEBUG'))


def connect_db():
    return sqlite3.connect(DATABASE)


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def query_db(db, query, args=(), one=False):
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def alter_db(db, query, args=()):
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


def get_user_info(db, username):
    user_res = query_db(db, "SELECT * FROM user WHERE username = '%s';" % username)
    if not user_res:
        return -1
    return user_res[0][0], user_res[0][1]


def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    with app.app_context():
        db = connect_db()
        with app.open_resource(CREATE_DB, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
