select TO_CHAR(p.post_date, 'Mon-YYYY') as p_month, p.num_upvotes as p_upvotes, avg(p.sentiment_score) as p_sent, avg(C1.total_comments) as t_comments
	from post p join
		( select c.post_id as p_id, count(*) as total_comments
			from comment c
			group by p_id) as C1 on C1.p_id = p.post_id
	where p.subreddit_name = '{}'
	group by p_month, p.num_upvotes
	having p.num_upvotes = max(p.num_upvotes)