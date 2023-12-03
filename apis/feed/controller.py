from flask import Blueprint, request
import json
from apis.feed.service import get_feed, search_news

api_feed = Blueprint('api_feed', __name__)


@api_feed.route('/feed', methods=['GET'])
def index():
    feed_type = request.args.get('type')
    feed = get_feed(feed_type)
    if feed is None:
        res = {
            'status': 0,
            'message': '稍后再试',
            'data': []
        }
    else:
        res = {
            'status': 1,
            'message': 'success',
            'data': feed
        }

    return json.dumps(res, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}


@api_feed.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    news = search_news(query)
    print(news)
    if news is None:
        res = {
            'status': 0,
            'message': '稍后再试',
            'data': []
        }
    else:
        res = {
            'status': 1,
            'message': 'success',
            'data': news
        }
    return json.dumps(res, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}
