CREATE TABLE Comments (
    comment_id SERIAL PRIMARY KEY,
    comment_text VARCHAR(100),
    comment_date TIMESTAMP,
    post_id SERIAL REFERENCES Post(post_id),
    subreddit_name VARCHAR(50) REFERENCES Subreddit(subreddit_name),
    comment_op VARCHAR(50),
    num_upvotes INTEGER,
    sentiment_score REAL,
    stock_symbols VARCHAR(200)
);