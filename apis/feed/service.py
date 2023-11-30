import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import datetime
from dbmanager import mymongo as mongo, mypinecone as pinecone
import math


def get_date_range(period):
    today = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    if period == 'daily':
        start_date = today - datetime.timedelta(days=2)
    elif period == 'weekly':
        start_date = today - datetime.timedelta(days=7)
    elif period == 'monthly':
        start_date = today - datetime.timedelta(days=30)
    else:
        return None
    return start_date.timestamp(), today.timestamp()


def get_feed(period):
    start_date, end_date = get_date_range(period)
    filter = {
        'start_date': start_date,
        'end_date': end_date,
        'period': period
    }
    mongo_query = mongo.client['NewsSnap']['feed'].find_one(
        filter)
    if mongo_query is not None:

        return mongo_query['feed']

    df = get_news_by_date(start_date, end_date)
    centers = cluster_news(df)
    feeds = get_news_by_vectors(centers, 100, period)
    # 将今天的feed_ids存入数据库
    mongo.client['NewsSnap']['feed'].insert_one({
        'feed': feeds,
        'start_date': start_date,
        'end_date': end_date,
        'period': period
    })

    return feeds


def get_news_by_vectors(tagged_vectors, limit=100, period='daily'):
    avg_n_news_per_tag = math.ceil(limit / len(tagged_vectors))
    start_date, end_date = get_date_range(period)
    filters = {
        'date': {'$gte': start_date, '$lte': end_date},
    }
    for tag in tagged_vectors:
        news_list = []
        avg_n_news_per_vector = math.ceil(
            avg_n_news_per_tag / len(tagged_vectors[tag]))
        for vectors in tagged_vectors[tag]:
            news = pinecone.query(
                vector=vectors,
                k_top=avg_n_news_per_vector,
                filter=filters,
                include_metadata=True,
                include_values=False
            )

            for news_item in news:
                data = {
                    'id': news_item['id'],
                    'title': news_item['metadata']['title'],
                    'link': news_item['metadata']['link'],
                    'source': news_item['metadata']['source'],
                    'date': news_item['metadata']['date'],
                    'score': news_item['score'],
                    'ai_summary': news_item['metadata']['ai_summary'],
                    'author': news_item['metadata']['author'],
                }
                news_list.append(data)
        tagged_vectors[tag] = news_list
    return tagged_vectors


def best_n_clusters(matrix, max_clusters=10):
    if len(matrix) < max_clusters:
        max_clusters = len(matrix)
    scores = []
    for n_clusters in range(2, max_clusters):
        kmeans = KMeans(n_clusters=n_clusters, random_state=0,
                        n_init='auto').fit(matrix)
        score = silhouette_score(matrix, kmeans.labels_)
        scores.append(score)
    return scores.index(max(scores))+2 if scores else len(matrix)


def cluster_news(df):
    centers = {}
    vecotrs = np.array(df['embedding'].tolist())
    n_cluster = best_n_clusters(vecotrs, 15)
    k_means = KMeans(n_clusters=n_cluster, random_state=42,
                     n_init='auto').fit(vecotrs)
    # 一次聚类结果
    df['cluster'] = k_means.labels_
    # 二次聚类 将每个类再聚成子类 提取子类center
    for i in range(n_cluster):
        # 选择类别为i的新闻
        cluster = df[df['cluster'] == i].copy()
        sub_vectors = np.array(cluster['embedding'].tolist())
        sub_n_cluster = best_n_clusters(sub_vectors, 20)
        # # 开始聚类
        sub_k_means = KMeans(n_clusters=sub_n_cluster, random_state=42,
                             n_init='auto').fit(sub_vectors)
        cluster['sub_cluster'] = sub_k_means.labels_
        cluster['distance'] = sub_k_means.transform(
            sub_vectors).min(axis=1)
        cluster_head = cluster.sort_values(
            by=['sub_cluster', 'distance'], ascending=True).groupby('sub_cluster').head(1)
        desc = get_descs_abstract(cluster_head['title'].tolist())
        centers[desc] = sub_k_means.cluster_centers_.tolist()

    return centers


def get_descs_abstract(titles):
    # TODO 用title生成类特征
    # 暂时先用第一条新闻的title

    return titles[0]


def get_news_by_date(start_date, end_date, limit=1000):
    # 需要传入的参数
    # 日期开始时间戳
    # 日期结束时间戳
    # limit 限制返回的数量
    # page 页数
    try:
        vector = [0.2]*1536
        filters = {
            'date': {'$gte': start_date, '$lte': end_date},
        }
        news = pinecone.query(
            vector=vector,
            k_top=limit,
            filter=filters,
            include_metadata=True,
            include_values=True
        )
        df = pd.DataFrame([news_item['metadata'] for news_item in news])
        df['score'] = [news_item['score'] for news_item in news]
        df['embedding'] = [news_item['values'] for news_item in news]
        df.drop(columns=['source', 'author',
                'link', 'ai_summary'], inplace=True)
        # 把socre放到第一列
        cols = list(df.columns)
        cols.insert(0, cols.pop(cols.index('score')))
        df = df.loc[:, cols]
        return df

    except Exception as e:
        return None


# if __name__ == '__main__':
#     get_feed('daily')
