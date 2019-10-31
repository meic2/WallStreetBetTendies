import collections
import datetime
import json
import praw
import psycopg2
import requests
import urllib


def load_reddit_credentials():
    with open('reddit_credentials.json') as f:
        reddit_credentials = json.load(f)
    return reddit_credentials


def upload_subreddit_data(reddit, subreddit_name, conn):
    subreddit = reddit.subreddit(subreddit_name)
    num_subscribers = subreddit.subscribers
    overview = subreddit.public_description
    print(subreddit_name, num_subscribers, overview)

    cur = conn.cursor()

    cur.execute('UPDATE Subreddit SET num_followers={} WHERE subreddit_name=\'{}\''.format(num_subscribers, subreddit_name))
    cur.execute(
        'INSERT INTO Subreddit (subreddit_name, num_followers, overview) SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Subreddit WHERE subreddit_name = %s)',
        (subreddit_name, num_subscribers, overview, subreddit_name)
    )
    conn.commit()

    cur.close()


def upload_subreddit_posts_and_comments(reddit, subreddit_name, conn):
    subreddit = reddit.subreddit(subreddit_name)
    cur = conn.cursor()

    for post in subreddit.hot(limit=10):
        # print('Post info: ', post.id, post.title, post.created_utc, post.score)
        # print('Post description: ', post.selftext)
        # print('Post comments: ', post.comments)
        post_time = datetime.datetime.fromtimestamp(post.created_utc)
        post_comments = post.comments

        cur.execute(
            'UPDATE Post SET num_upvotes={} WHERE post_id=\'{}\''.format(post.score, post.id)
        )
        cur.execute(
            'INSERT INTO Post (post_id, post_title, post_description, post_date, subreddit_name, post_op, num_upvotes) SELECT %s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Post WHERE post_id = %s)',
            (post.id, post.title, post.selftext, post_time, subreddit_name, post.author.name, post.score, post.id))
        conn.commit()

        for top_level_comment in post.comments:
            # TODO: Expand MoreComments objects to get ALL comments of post
            if isinstance(top_level_comment, praw.models.MoreComments):  # Skip comments with replies for now
                continue

            top_level_comment_time = datetime.datetime.fromtimestamp(top_level_comment.created_utc)
            if not top_level_comment.author:
                top_level_comment_op = '[None]'
            else:
                top_level_comment_op = top_level_comment.author.name

            cur.execute(
                'UPDATE Comment SET num_upvotes={} WHERE comment_id=\'{}\''.format(top_level_comment.score, top_level_comment.id)
            )
            cur.execute(
                'INSERT INTO Comment (comment_id, comment_text, comment_date, post_id, subreddit_name, comment_op, num_upvotes) SELECT %s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM Comment WHERE comment_id = %s)',
                (top_level_comment.id, top_level_comment.body,
                 top_level_comment_time, post.id, subreddit_name,
                 top_level_comment_op, top_level_comment.score, top_level_comment.id))

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
# subreddits = ['business']
for subreddit_name in subreddits:
    upload_subreddit_data(reddit_auth, subreddit_name, conn)
    upload_subreddit_posts_and_comments(reddit_auth, subreddit_name, conn)
