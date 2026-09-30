--a) Order totals
SELECT 
    COUNT(*) AS total_orders,
    SUM(p.price * o.quantity * (1 - IFNULL(o.discount_pct,0)/100.0)) AS total_revenue,
    AVG(p.price * o.quantity * (1 - IFNULL(o.discount_pct,0)/100.0)) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;


--b) COUNT(*) vs COUNT(column)
SELECT COUNT(*), COUNT(rating), COUNT(*)-COUNT(rating) AS difference 
FROM orders;
--c) LEFT JOIN with a genuine zero-match row
SELECT c.customer_id,c.name
FROM customers c LEFT JOIN orders o ON c.customer_id=o.customer_id
GROUP BY c.name
HAVING COUNT(order_id)=0;
--another method
SELECT customer_id, name
FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM orders);
--d) GROUP BY + HAVING
SELECT 
    c.city,
    COUNT(*) AS total_orders,
    COUNT(CASE WHEN o.returned = 1 THEN 1 END) AS returned_orders,
    ROUND(
        COUNT(CASE WHEN o.returned = 1 THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) AS return_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20;

--e) Ranking with ORDER BY + LIMIT/OFFSET
-- Top 5
SELECT c.customer_id, c.name,
       SUM(p.price * o.quantity * (1 - IFNULL(o.discount_pct,0)/100.0)) AS total_spend
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC
LIMIT 5;

-- Ranks 3–5
SELECT c.customer_id, c.name,
       SUM(p.price * o.quantity * (1 - IFNULL(o.discount_pct,0)/100.0)) AS total_spend
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC
LIMIT 3 OFFSET 2;
--f) Three-table JOIN with GROUP BY
SELECT p.category,
       COUNT(o.order_id) AS order_count,
       SUM(p.price * o.quantity * (1 - IFNULL(o.discount_pct,0)/100.0)) AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY p.category;
--g) LIKE pattern match
SELECT customer_id, name
FROM customers
WHERE name LIKE 'A%';
--i) ALTER TABLE + UPDATE with CASE
SELECT DISTINCT acquisition_source
FROM customers;

ALTER TABLE customers ADD COLUMN loyalty_tier TEXT;

UPDATE customers
SET loyalty_tier = CASE 
    WHEN city IN ('Delhi','Mumbai','Bangalore','Chennai') THEN 'Gold'
    ELSE 'Silver'
END;
