from flask import blueprints, request
from apis.search.service import search
import json

api_search = blueprints.Blueprint('api_search', __name__)

@api_search.route('/search', methods=['GET'])
def search_api():
    query = request.args.get('query')
    page = request.args.get('page')
    print(query)
    print(page)
    if not page:
        page = 1
    else:
        page = int(page)
    result = search(query, page)
    print(type(result))
    return json.dumps(result, ensure_ascii=False).encode('utf8'), 200, {'Content-Type': 'application/json; charset=utf-8'}