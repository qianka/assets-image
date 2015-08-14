# -*- coding: utf-8 -*-

import imghdr, io, time, os, json, base64, hmac, urllib

from flask import Flask
from flask import render_template, abort, request, jsonify
from PIL import Image
import upyun

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')

upyun_bucket = app.config["BUCKET"]
upyun_username = app.config["USERNAME"]
upyun_password = app.config["PASSWD"]
URL_PREFIX = app.config["URL"]

app.up = upyun.UpYun(upyun_bucket,
                     upyun_username,
                     upyun_password,
                     timeout=30,
                     endpoint=upyun.ED_AUTO)

#
# error handlers
#
@app.errorhandler(400)
def custom400(error):
    response = jsonify({'message': error.description})
    return response

@app.errorhandler(403)
def custom403(error):
    response = jsonify({'message': error.description})
    return response

@app.errorhandler(500)
def custom500(error):
    response = jsonify({'message': error.description})
    return response

#
# internal functions
#
def _md5(data):
    import hashlib
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

def create(data):

    # data = request.stream.read()

    size = len(data)

    if size <= 0:
        abort(403, 'no body')

    ext = str(imghdr.what(None, h=data)).lower()
    if not ext:
        abort(403, 'no valid type')

    with Image.open(io.BytesIO(data)) as im:
        width, height = im.size

    hashcode = _md5(data)
    url = '%s/%s.%s' % (URL_PREFIX, hashcode, ext)
    rv = {
        'hash': hashcode,
        'ext': ext,
        'width': width,
        'height': height,
        'size': size,
        'url': url
    }
    app.logger.debug(rv)

    filename = '/%s.%s' % (hashcode, ext)
    try:
        app.up.put(filename, data)
        return jsonify(rv)
    except Exception as e:
        app.logger.error(e)
        abort(500, 'error when uploading to upyun')


def get():
    pass


def delete():
    pass


#
# routes
#
# @app.route('/', methods=['POST'])
# def items():
#     # curl -v 'http://127.0.0.1:5000' --data-binary '@/Users/shrimp/Desktop/chrom.png'
#     return create()
#
# @app.route('/<name>', methods=['GET', 'DELETE'])
# def item(name):
#     if request.method == 'GET':
#         return get()
#     if request.method == 'DELETE':
#         return delete()
#     abort(403, 'oops')

@app.route("/")
def account():
    return render_template('uploads.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['mypic']
    if file:
        data = file.read()
        return create(data)