from flask import Blueprint

default_bp = Blueprint('default_bp',
                       __name__)


@default_bp.route('/')
def default():
    return 'Perseus is UP'

@default_bp.route('/api/v1/status')
def api_default():
    return {'status': 'OK'}