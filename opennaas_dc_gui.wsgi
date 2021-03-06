#!/usr/bin/python

from flask import Flask
import sys,logging
import settings
#logging.basicConfig(stream=sys.stderr)
from wsgi import wsgi_app

app = Flask(__name__ , static_url_path='')
app.register_blueprint(wsgi_app)
app.debug = True

if __name__ == "__main__":
    app.run(host = settings.WSGI_host , port = settings.WSGI_port)
