from flask import Blueprint, request
import json
from apis.feed.service import get_feed

api_feed = Blueprint('api_feed', __name__)


@api_feed.route('/feed', methods=['GET'])
def index():
    feed_type = request.args.get('type')
    try:
        news = get_feed(feed_type)
        status = 1
        message = 'success'
    except Exception as e:
        print(e)
        news = []
        status = 0
        message = '稍后再试'

    n = 0
    for i in news:
        length_news = len(news[i])
        n += length_news
    res = {
        'status': status,
        'message': message,
        'total': n,
        'news': news
    }

    return json.dumps(res, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}
