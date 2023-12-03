import logging
from dbmanager import mymongo, mypinecone, myopenai
from bson import json_util
import json

def get_feed(type):
    try:
        feed = mymongo['NewsSnap']['feeds'].find({
            'period': type
        }).sort({'created_at': -1}).limit(1)
        feed = list(feed)[0]
        if not feed or not feed['feed']:
            return None
        feed = feed
        return json.loads(json_util.dumps(feed))
    except Exception as e:
        logging.error(e)
        return None


def search_news(query):
    try:
        embedding = myopenai.get_embedding(query)
        query = mypinecone.query(embedding, top_k=10, include_metadata=True)
        query = query['matches']
        res = []
        for item in query:
            res.append({
                'id': item['id'],
                'score': item['score'],
                'metadata': item['metadata']
            })
        
        return res
    except Exception as e:
        logging.error(e)
        return None
