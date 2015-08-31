# -*- coding: utf-8 -*-
import imghdr
import io
import os

from flask import Flask
from flask import abort, request, jsonify, render_template
from PIL import Image
import upyun


def raise_error(msg):
    raise RuntimeError(msg)


upyun_bucket   = os.environ.get('UPYUN_BUCKET')   or raise_error('environ')
upyun_username = os.environ.get('UPYUN_USERNAME') or raise_error('environ')
upyun_password = os.environ.get('UPYUN_PASSWORD') or raise_error('environ')
STORAGE_PREFIX = os.environ.get('STORAGE_PREFIX') or 'images'
URL_PREFIX     = os.environ.get('URL_PREFIX')     or ''


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


def create(data=None):
    if data is None:
        data = request.stream.read()

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

    filename = '/%s/%s.%s' % (STORAGE_PREFIX, hashcode, ext)
    try:
        app.up.put(filename, data)
        return jsonify(rv)
    except Exception as e:
        app.logger.error(e)
        abort(500, 'error when uploading to upyun')


def get(name):
    pass


def delete(name):
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
        return get(name)
    if request.method == 'DELETE':
        return delete(name)
    abort(403, 'oops')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    print(request.method)
    if request.method == 'GET':
        return render_template('upload.html')

    file = request.files['mypic']
    if file:
        data = file.read()
        return create(data)
