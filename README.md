# Quick Start

envrionment variables

```
UPYUN_BUCKET=your_upyun_bucker
UPYUN_USERNAME=your_upyun_username
UPYUN_PASSWORD=your_upyun_password
STORAGE_PREFX=images
```

```
$ ve pip install -r requirements.txt
$ ve python run.py
```

run with `uwsgi`

```
$ ve uwsgi --http-socket 0.0.0.0:5000 --wsgi-file server.py --callable app --processes 5 --max-requests 100
```

upload with `curl`

```
$ curl -v 'http://127.0.0.1:5000' --data-binary '@/path/to/image.jpg'
```
