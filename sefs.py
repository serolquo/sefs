# all the imports
import os
import hashlib
import base64
from random import SystemRandom 

import sqlite3

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from flask.ext import restful
from flask.ext.restful import reqparse, Api
from flask.ext.sqlalchemy import SQLAlchemy

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.bucket import Bucket

from utils import RandomString
from models import UserFile


basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), './')


app = Flask(__name__)
app.config.from_object('config')


# flask-sqlalchemy
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sefs.db')
#db = SQLAlchemy(app)

# flask-restful
#api = restful.Api(app)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


#import views


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_home():
    blah = UserFile(None)
    return render_template(
                            'index.html', 
                            user_file=blah,
                            signed_policy=blah.sign_policy(app.config['S3_SECRET_KEY']),
                            access_key=app.config['S3_ACCESS_KEY'])

@app.route('/get/<string:s3_file>', methods=['GET'])
@app.route('/get/', methods=['GET'])
def show_get(s3_file=None):
    return render_template('get.html',file_index=s3_file)


@app.route('/get_signed_url/<string:s3_file>', methods=['GET'])
def show_get_signed_url(s3_file=None):
    user_file = UserFile(s3_file)
    if user_file.s3_object is not None:
            
        s3_conn = S3Connection(app.config['S3_ACCESS_KEY'],app.config['S3_SECRET_KEY'])
        s3_bucket = Bucket(s3_conn,'sefss')
        s3_key = Key(s3_bucket)
        s3_key.key = user_file.s3_object
        url = s3_conn.generate_url(
    120,'GET','sefss',s3_key.key
    )
        return url
    else:
        return None


@app.route('/uploaded/<string:s3_file>')
def show_uploaded(s3_file):
    result = g.db.execute('select * from entries where s3_object = ?',(s3_file,))
    row = result.fetchone()
    if row is not None:
        g.db.execute('update entries set uploaded=1 where s3_object = ?',(s3_file,))
        g.db.commit()
        return render_template('uploaded.html',msg='File uploaded')
    else:
        return render_template('uploaded.html',msg='File not uploaded')
    

if __name__ == '__main__':
    app.run()
