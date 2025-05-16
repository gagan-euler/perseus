from flask import Flask
from threading import Thread

from perseus.blueprints.api.default import default_bp
from perseus.blueprints.api.pull import pull_bp
from perseus.blueprints.api.push import push_bp

from perseus.blueprints.common import params


class Perseus:
    def __init__(self):
        self._app = Flask(__name__)

        self._app.register_blueprint(push_bp)
        self._app.register_blueprint(pull_bp)
        self._app.register_blueprint(default_bp)

    def run(self):
        app = Thread(target=self._app.run(params.ip, params.port))
        app.start()
