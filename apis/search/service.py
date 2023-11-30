from dbmanager import mymongo as mongo, mypinecone as pinecone, myopenai as openai

def search(search_input, page):
    limit = 20
    start = (page - 1) * limit
    end = start + limit
    query_embedding = openai.get_embedding(search_input)
    res = pinecone.query(
        vector=query_embedding,
        k_top=end,
        include_metadata=True,
        include_values=False
    )
    news_list = []
    for news_item in res[start:end]:
                data = {
                    'title': news_item['metadata']['title'],
                    'link': news_item['metadata']['link'],
                    'source': news_item['metadata']['source'],
                    'date': news_item['metadata']['date'],
                    'score': news_item['score'],
                    'ai_summary': news_item['metadata']['ai_summary'],
                    'author': news_item['metadata']['author'],
                }
                news_list.append(data)
    return news_list
