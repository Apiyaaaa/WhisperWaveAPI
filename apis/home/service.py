import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import datetime
from dbmanager import mymongo as db, mypinecone


def get_today_feed():
    # 获取当前日期0点时间戳
    date = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    filter = {
        'date': {'$gte': date.timestamp()}
    }
    # 从数据库中查找是否已经有今天的feed_ids
    feed_ids_doc = db.client['NewsSnap']['feed_ids'].find_one(filter)
    # 如果数据库中已经有今天的feed_ids，直接返回
    if feed_ids_doc is not None:
        feed_ids = feed_ids_doc['feed_ids']
        return feed_ids
    # 获取今天0点的时间戳
    today_start = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    # 获取三天前0点的时间戳
    yesterday_start = today_start - datetime.timedelta(days=3)
    # 获取三天前到今天的新闻
    news = get_news_by_date(yesterday_start.timestamp(),
                            today_start.timestamp())
    # 如果没有新闻，返回空列表
    if not news:
        return []
    # 对新闻进行聚类
    news = cluster_news(news)
    # 对每个聚类，获取新闻详情
    for i in news:
        i['news'] = get_news_by_ids(i['news'])
    # 将今天的feed_ids存入数据库
    db.client['NewsSnap']['feed_ids'].insert_one({
        'feed_ids': news,
        'date': today_start.timestamp()
    })
    # 返回今日新闻推送
    return news


def get_news_by_ids(ids):
    projection = {
        'embedding': 0,
        'content': 0,
    }
    news = db.client['NewsSnap']['news'].find(
        {'_id': {'$in': ids}}, projection)
    return list(news)


def get_news_by_date(start_date, end_date):
    projection = {
        'embedding': 1,
        'title': 1,
    }
    news = db.client['NewsSnap']['news'].find({'date': {'$gte': start_date, '$lte': end_date},
                                               'embedding': {'$ne': None}}, projection)
    return list(news)


def cluster_news(news):
    if len(news) < 2:
        return news
    news = pd.DataFrame(news).drop_duplicates(subset=['title'])
    result = pd.DataFrame()
    matrix = np.array(news['embedding'].tolist())
    n_cluster = best_n_clusters(matrix, 15)
    k_means = KMeans(n_clusters=n_cluster, random_state=42,
                     n_init='auto').fit(matrix)
    # 一次聚类结果
    news['cluster'] = k_means.labels_
    # 二次聚类 将每个类再聚成子类 并且把每个子类的第一个新闻提出来
    # 如果总新闻数为50 计算每个类需要多少feature news
    n_feature_news = int(50 / n_cluster)
    for i in range(n_cluster):
        # 选择类别为i的新闻
        cluster = news[news['cluster'] == i].copy()
        # print(cluster)

        sub_n_cluster = best_n_clusters(
            np.array(cluster['embedding'].tolist()), n_feature_news)
        # # 开始聚类
        sub_k_means = KMeans(n_clusters=sub_n_cluster, random_state=42,
                             n_init='auto').fit(np.array(cluster['embedding'].tolist()))
        cluster['sub_cluster'] = sub_k_means.labels_
        cluster['distance'] = sub_k_means.transform(
            np.array(cluster['embedding'].tolist())).min(axis=1)
        cluster = cluster.sort_values(
            by=['sub_cluster', 'distance'], ascending=True)
        # 把每个子类的distance最小的新闻提出来 直到提出n_feature_news条
        feature_news = cluster.groupby('sub_cluster').head(
            int(n_feature_news/sub_n_cluster))
        # 添加到result中
        result = pd.concat([result, feature_news])
    # 根据cluster 返回2d array
    result = result.groupby('cluster')['_id'].agg(
        list).reset_index(name='news')
    return result.to_dict('records')


def best_n_clusters(matrix, max_cluster=15):
    if len(matrix) < max_cluster:
        max_cluster = len(matrix)
    scores = []
    for i in range(2, max_cluster):
        kmeans = KMeans(n_clusters=i, random_state=42,
                        n_init='auto').fit(matrix)
        score = silhouette_score(matrix, kmeans.labels_)
        scores.append(score)
    return np.argmax(scores) + 2 if scores else len(matrix)
