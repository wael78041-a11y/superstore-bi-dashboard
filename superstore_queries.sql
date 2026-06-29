-- superstore sales analysis
-- sqlite via db browser
-- 9994 rows, 21 columns after cleaning


-- how i loaded the data from python:
-- import sqlite3
-- conn = sqlite3.connect('superstore.db')
-- df.to_sql('superstore', conn, if_exists='replace', index=False)
-- conn.close()


-- query 1: sales and profit by category
-- wanted to see which category makes the most money
-- turns out technology leads in both sales and profit
-- furniture has surprisingly weak profit despite high sales

select 
    category,
    round(sum(sales), 2)  as total_sales,
    round(sum(profit), 2) as total_profit
from superstore
group by category
order by total_sales desc;

-- technology      836154    145454
-- furniture       741999     18451   <- high sales but terrible margin
-- office supplies 719047    122490


-- query 2: regional performance
-- added profit margin % to see which region is actually efficient
-- central has more sales than south but worse margin, interesting

select 
    region,
    round(sum(sales), 2)                      as total_sales,
    round(sum(profit), 2)                     as total_profit,
    round(sum(profit) / sum(sales) * 100, 1) as profit_margin_pct
from superstore
group by region
order by total_profit desc;

-- west     725457    108418    14.9%
-- east     678781     91522    13.5%
-- south    391721     46749    11.9%
-- central  501239     39706     7.9%  <- worst margin


-- query 3: discount vs profit
-- used case when to bucket discounts into ranges (similar to pd.cut in python)
-- the results here were pretty alarming

select 
    case 
        when discount <= 0.1 then '0-10%'
        when discount <= 0.3 then '10-30%'
        when discount <= 0.5 then '30-50%'
        else '50%+'
    end as discount_range,
    round(avg(profit), 2) as avg_profit,
    count(*)              as num_orders
from superstore
group by discount_range
order by avg_profit desc;

-- 0-10%      67.46    4892
-- 10-30%     20.68    3936
-- 50%+      -89.44     856
-- 30-50%   -156.28     310  <- losing money on every order with 30%+ discount


-- query 4: monthly sales
-- strftime extracts the month from the date column
-- cast to integer so it sorts correctly as a number not text

select 
    cast(strftime('%m', "Order Date") as integer) as month,
    round(sum(sales), 2)                          as total_sales,
    round(sum(profit), 2)                         as total_profit
from superstore
group by month
order by total_sales desc;

-- month 11   352461    35468  <- november is the peak
-- month 12   325293    43369
-- month 9    307649    36857
-- month 2     59751    10294  <- february is the slowest by far