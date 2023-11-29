from pymongo import MongoClient
import pinecone
import os
import openai

class MyOpenAI:
    def __init__(self, openai_key):
        openai.api_key = openai_key
        self.summary_model = 'gpt3.5-turbo'


class MyMongo:
    _instance = None

    def __new__(cls, uri=None):
        if cls._instance is None:
            cls._instance = super(MyMongo, cls).__new__(cls)
            cls.client = MongoClient(uri)
            return cls._instance

    def __del__(self):
        self.client.close()

    def get_db(self, db_name):
        return self.client[db_name]


class PineconeM:
    def __init__(self, pinecone_key):
        pinecone.init(api_key=pinecone_key,
                      environment="gcp-starter")
        self.index = pinecone.Index("newssnap-test")

    def insert(self, id, vector, metadata):
        try:
            self.index.upsert([(id, vector, metadata)])
        except Exception as e:
            print(e)
            return False

        return True

    def query(self, vector, k_top=10, filter=None, include_metadata=True, include_values=False):
        try:
            res = self.index.query(
                vector=vector,
                top_k=k_top,
                filter=filter,
                include_metadata=include_metadata, include_values=include_values)
        except Exception as e:
            print('error', e)
            return None

        return res['matches']


mypinecone = PineconeM(os.getenv('PINECONE_KEY'))
mymongo = MyMongo(os.getenv('MONGODB_URI'))
