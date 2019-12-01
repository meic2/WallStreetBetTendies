import collections
import datetime
import json
import praw
import psycopg2
import requests
from textblob import TextBlob
import time
import urllib

# TODO:
# 1. Figure out why uploading subreddit posts and comments is fucking failing. FUCKING BULLSHIT
# 2. Get most frequent keywords and its respective counts and upload to MongoDB
# 3. Compute sentiment of posts' titles and comments and add to insert query
# 4. Write skeleton for URL endpoints (one for each SQL query) and email Alexi to write SQL queries


def load_reddit_credentials():
    with open('data_scripts/reddit_credentials.json') as f:
        reddit_credentials = json.load(f)
    return reddit_credentials


def upload_subreddit_data(reddit, subreddit_name, conn):
    subreddit = reddit.subreddit(subreddit_name)
    num_subscribers = subreddit.subscribers
    overview = subreddit.public_description

    cur = conn.cursor()

    try:
        cur.execute('UPDATE Subreddit SET num_followers={} WHERE subreddit_name=\'{}\''.format(num_subscribers, subreddit_name))
        cur.execute(
            'INSERT INTO Subreddit (subreddit_name, num_followers, overview) SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Subreddit WHERE subreddit_name = %s)',
            (subreddit_name, num_subscribers, overview, subreddit_name)
        )
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print('ERROR with uploading subreddit data: ', str(error))

    print('Uploaded subreddit info: ', subreddit_name, num_subscribers, overview)

    cur.close()


def upload_post(post, subreddit_name, cur):
    # print('Post info: ', post.id, post.title, post.created_utc, post.score)
    # print('Post description: ', post.selftext)
    # print('Post comments: ', post.comments)
    post_time = datetime.datetime.fromtimestamp(post.created_utc)
    post_comments = post.comments
    if not post.author:  # In case account no longer exists
        post_op = '[None]'
    else:
        post_op = post.author.name
    post_sentiment = (TextBlob(post.title).polarity * 0.7) + (TextBlob(post.selftext).polarity * 0.3)

    try:
        cur.execute(
            'UPDATE Post SET num_upvotes={} WHERE post_id=\'{}\''.format(post.score, post.id)
        )
        cur.execute(
            'INSERT INTO Post (post_id, post_title, post_description, post_date, subreddit_name, post_op, num_upvotes, sentiment_score) SELECT %s, %s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Post WHERE post_id = %s)',
            (
                post.id, 
                post.title, 
                post.selftext,
                post_time, 
                subreddit_name, 
                post_op, 
                post.score,
                post_sentiment,
                post.id
            )
        )
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print('ERROR with uploading posts\' data of subreddit {}: {}'.format(subreddit_name, str(error)))


def upload_comments(post, subreddit_name, cur):
    for comment in post.comments:
        comment_time = datetime.datetime.fromtimestamp(comment.created_utc)
        if not comment.author:  # In case account no longer exists
            comment_op = '[None]'
        else:
            comment_op = comment.author.name
        comment_sentiment = TextBlob(comment.body).polarity

        try:
            cur.execute(
                'UPDATE Comment SET num_upvotes={} WHERE comment_id=\'{}\''.format(comment.score, comment.id)
            )
            cur.execute(
                'INSERT INTO Comment (comment_id, comment_text, comment_date, post_id, subreddit_name, comment_op, num_upvotes, sentiment_score) SELECT %s, %s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Comment WHERE comment_id = %s)',
                (
                    comment.id, 
                    comment.body,
                    comment_time, 
                    post.id, 
                    subreddit_name,
                    comment_op, 
                    comment.score, 
                    comment_sentiment,
                    comment.id
                )
            )
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print('ERROR with uploading comments\' data of subreddit {}: {}'.format(subreddit_name, str(error)))
            raise Exception(error)


def upload_subreddit_posts_and_comments(reddit, subreddit_name, conn):
    subreddit = reddit.subreddit(subreddit_name)
    cur = conn.cursor()

    # Get all the top posts of subreddit from past year
    top_posts_past_year = subreddit.top(time_filter='year', limit=100)
    for post in top_posts_past_year:
        upload_post(post, subreddit_name, cur)
        print('Uploaded post info: ', post.title)
        post.comments.replace_more(limit=0)  # Get all top-level comments (replace all MoreComments objs with Comment obj)
        upload_comments(post, subreddit_name, cur)
        print('Uploaded all top-level comments of above post')

    cur.close()


reddit_creds = load_reddit_credentials()
reddit_auth = praw.Reddit(
    client_id=reddit_creds['client_id'],
    client_secret=reddit_creds['client_secret'],
    user_agent=reddit_creds['user_agent']
)
conn = psycopg2.connect(
    host="fa19-cs411-048.cs.illinois.edu",
    database="wsb_tendies",
    user="wsb_django_user",
    password="411_wsb_tendies"
)

subreddits = ['investing', 'stocks', 'wallstreetbets', 'StockMarket', 'economy']
for subreddit_name in subreddits:
    start_time = time.time()
    upload_subreddit_data(reddit_auth, subreddit_name, conn)
    upload_subreddit_posts_and_comments(reddit_auth, subreddit_name, conn)
    end_time = time.time()
    print('Time taken to upload all subreddit data for {}: {}', subreddit_name, str(end_time - start_time))