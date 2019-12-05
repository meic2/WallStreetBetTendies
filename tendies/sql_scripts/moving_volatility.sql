CREATE OR REPLACE FUNCTION calVolatility2(dateStart timestamp without time zone, 
										 dateEnd timestamp without time zone) 
	RETURNS table (j json) 	AS 

	$$
	BEGIN
	RETURN QUERY
	
	WITH derived AS (
	select stock_symbol, ts, close_price, log( close_price / price_prev ) as return
	from (
	select stock_symbol
	    , ts
	    , close_price
	    , (
	         select close_price
	         from stocktickdata b
	         where b.stock_symbol = a.stock_symbol
	         and b.ts < a.ts
	         order by b.ts desc
	         limit 1
	      ) as price_prev
	from stocktickdata AS a
	) derived
	),
	
	moving_volatility as (
		SELECT stock_symbol, ts,
		
		CASE WHEN
		
			ROW_NUMBER() OVER (
					PARTITION BY stock_symbol
					ORDER BY ts) > 9 
			THEN
			 stddev_samp(return) OVER (PARTITION BY stock_symbol ORDER BY ts
										ROWS BETWEEN 10 PRECEDING AND CURRENT ROW)
								
			END AS moving_10_volatility,
		
		CASE WHEN
			ROW_NUMBER() OVER (
					PARTITION BY stock_symbol
					ORDER BY ts) > 29
			THEN
			 stddev_samp(return) OVER (PARTITION BY stock_symbol ORDER BY ts
										ROWS BETWEEN 30 PRECEDING AND CURRENT ROW)
								
			END AS moving_30_volatility
			FROM derived)

		SELECT row_to_json(a) FROM (SELECT * FROM moving_volatility) a;
	END;
	$$ LANGUAGE plpgsql;