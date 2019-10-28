CREATE TABLE Post (
    post_id SERIAL PRIMARY KEY,
    post_title VARCHAR(100),
    post_description VARCHAR(5000),
    post_tag VARCHAR(100),
    post_date TIMESTAMP,
    subreddit_name VARCHAR(50) REFERENCES Subreddit(subreddit_name),
    post_op VARCHAR(50),
    num_upvotes INTEGER,
    sentiment_score REAL,
    stock_symbols VARCHAR(200)
);