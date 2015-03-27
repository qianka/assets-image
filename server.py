# -*- coding: utf-8 -*-
import imghdr
import os

from flask import Flask
from flask import abort, request, jsonify
import upyun



VALID_TYPES = ('png', 'jpeg', 'jpg', 'svg')

def raise_error(msg):
    raise RuntimeError(msg)


upyun_bucket = os.environ.get('UPYUN_BUCKET') or\
               raise_error('environ')

upyun_username = os.environ.get('UPYUN_USERNAME') or\
                 raise_error('environ')

upyun_password = os.environ.get('UPYUN_PASSWORD') or\
                 raise_error('environ')

PREFIX = os.environ.get('STORAGE_PREFIX') or\
         raise_error('envrion')

app = Flask(__name__)

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

def create():

    data = request.stream.read()
    size = len(data)

    if size == 0:
        abort(403, 'no body')

    ext = str(imghdr.what('', h=data)).lower()

    if ext not in VALID_TYPES:
        abort(403, 'no valid type: %s' % ext)

    hash = _md5(data)
    name = "%s.%s" % (hash, ext)
    filename = '/%s/%s' % (PREFIX, name)
    rv = {'hash': hash, 'size': size, 'ext': ext, 'url': filename}
    app.logger.debug(rv)

    try:
        app.up.put(filename, data)
        return jsonify(rv)
    except Except as e:
        app.logger.error(e)
        abort(500, 'error when uploading to upyun')

def get():
    pass

def delete():
    pass

#
# routes
#
@app.route('/', methods=['POST'])
def items():
    return create()

@app.route('/<name>', methods=['GET', 'DELETE'])
def item(name):
    if request.method == 'GET':
        return get()
    if request.method == 'DELETE':
        return delete()
