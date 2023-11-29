from flask import Blueprint
from bson import json_util
from apis.home.service import get_today_feed

api_main = Blueprint('api_main', __name__)


@api_main.route('/news', methods=['GET'])
def index():
    news = get_today_feed()
    return json_util.dumps(news), 200
