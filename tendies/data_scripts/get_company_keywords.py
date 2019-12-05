import collections
import datetime
import pymongo
import requests


def get_company_most_common_keywords_res(company_name, subreddit, number_keyword=5):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    wsb_mongo_db = client['wsb_tendies']
    post_keywords_collection = wsb_mongo_db['post_keywords']
    
    # find all correlating post_ids
    try:
        company_ticker = requests.get('https://s.yimg.com/aq/autoc?query={}&region=US&lang=en-US'.format(company_name)).json()['ResultSet']['Result'][0]['symbol'].lower()
        print('company ticker: ', company_ticker)
    except:
        print('Company ticker not found')
        company_ticker = ''
    query = [
        {"$project": {"data": {"$objectToArray":"$keywords"}, "post_id": 1}},
        {"$unwind": "$data"},
        {"$match": {"data.k": company_name}},
        {"$project": {"post_id": 1, "_id":0}}
    ]

    document = post_keywords_collection.aggregate(query)
    list_post_id = []
    for post in document: 
        post_id = post['post_id'] 
        list_post_id.append(post_id)

    # find the corresponding keywords in the post_db
    query2 = [
        {"$match": {"post_id": {"$in": list_post_id}}},
        {"$project": {"data": {"$objectToArray":"$keywords"}, "subreddit_name": 1}},
        {"$unwind": "$data"},
        {"$group": {
            "_id" : {"keyword": "$data.k", 
                    "subreddit": "$subreddit_name"},
            "total" : {"$sum": "$data.v" },
        }},
        {"$project": {
            "total":1, 
            "keyword": "$_id.keyword",
            "subreddit": "$_id.subreddit",
            "_id": 0
        }},
        {"$match": {
            "keyword": {"$ne": ""}
        }},
        {"$sort": {"total": -1}}
    ]
    
    keyword_count = post_keywords_collection.aggregate(query2)

    subreddit_category = ['StockMarket', 'investing', 'economy', 'wallstreetbets', 'stocks']
    dict_keyword = {}

    #initialize the dictionary that hold the keyword 
    for subreddit in subreddit_category:
        dict_keyword[subreddit] = []

    common_stop_keywords = ['stock', 'price']
    #import data into the dictionary 
    for keyword_record in keyword_count: 
        subred = keyword_record['subreddit']
        count =  keyword_record['total']
        keyword =  keyword_record['keyword']
        if (len(dict_keyword[subred]) > number_keyword):
            continue
        if keyword != company_ticker or keyword != company_name or keyword not in common_stop_keywords:
            dict_keyword[subred].append({keyword: count})

    return dict_keyword


    