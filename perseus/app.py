from flask import Flask

from perseus.blueprints.api.default import default_bp
from perseus.blueprints.api.pull import pull_bp
from perseus.blueprints.api.push import push_bp
from perseus.blueprints.api.list import list_bp

from perseus.blueprints.common import params


class Perseus:
    def __init__(self):
        self._app = Flask(__name__)

        self._app.register_blueprint(push_bp)
        self._app.register_blueprint(pull_bp)
        self._app.register_blueprint(default_bp)
        self._app.register_blueprint(list_bp)

    def run(self):
        self._app.run(params.ip, params.port)

    def get_app(self):
        return self._app
