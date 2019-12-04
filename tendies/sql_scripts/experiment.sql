select allOther.p_sentiment, allOther.c_sentiment
from (
    select TO_CHAR(p.post_date,'Mon') as p_month, avg(p.sentiment_score) as p_sentiment, avg(c.sentiment_score) as c_sentiment
    from post p join comment c on p.post_id = c.post_id 
    where p.subreddit_name in ('investing','stocks','StockMarket','economy')
    group by p_month
) as allOther;