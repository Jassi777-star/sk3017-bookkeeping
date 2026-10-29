USE sk3017_bookkeeping;

INSERT IGNORE INTO categories (name, type, created_at) VALUES
  ('餐饮', 'expense', NOW()),
  ('交通', 'expense', NOW()),
  ('学习', 'expense', NOW()),
  ('娱乐', 'expense', NOW()),
  ('住房', 'expense', NOW()),
  ('医疗', 'expense', NOW()),
  ('其他支出', 'expense', NOW()),
  ('工资', 'income', NOW()),
  ('兼职', 'income', NOW()),
  ('理财', 'income', NOW()),
  ('其他收入', 'income', NOW());

SET @transaction_count = (SELECT COUNT(*) FROM transactions);

CREATE TEMPORARY TABLE seed_numbers (
  n INT PRIMARY KEY
);

INSERT INTO seed_numbers (n) VALUES
  (0),(1),(2),(3),(4),(5),(6),(7),(8),(9),
  (10),(11),(12),(13),(14),(15),(16),(17),(18),(19),
  (20),(21),(22),(23),(24),(25),(26),(27),(28),(29),
  (30),(31),(32),(33),(34),(35),(36),(37),(38),(39),
  (40),(41),(42),(43),(44),(45),(46),(47),(48),(49),
  (50),(51),(52),(53),(54),(55),(56),(57),(58),(59);

INSERT INTO transactions (
  type,
  category_id,
  amount,
  occurred_on,
  note,
  created_at,
  updated_at
)
SELECT
  CASE WHEN MOD(n, 12) < 10 THEN 'expense' ELSE 'income' END,
  (
    SELECT id
    FROM categories
    WHERE type = CASE WHEN MOD(n, 12) < 10 THEN 'expense' ELSE 'income' END
      AND name = CASE
        WHEN MOD(n, 12) < 10 THEN ELT(MOD(n, 5) + 1, '餐饮', '交通', '学习', '娱乐', '住房')
        WHEN MOD(n, 12) = 10 THEN '工资'
        ELSE '兼职'
      END
    LIMIT 1
  ),
  CASE
    WHEN MOD(n, 12) < 10 THEN 10 + MOD(n * 17, 90)
    WHEN MOD(n, 12) = 10 THEN 6500
    ELSE 800 + MOD(n * 23, 500)
  END,
  DATE_ADD(
    DATE_SUB(
      DATE_FORMAT(CURDATE(), '%Y-%m-01'),
      INTERVAL (4 - FLOOR(n / 12)) MONTH
    ),
    INTERVAL MOD(n * 3, 25) DAY
  ),
  CASE
    WHEN MOD(n, 12) = 10 THEN '月度工资'
    WHEN MOD(n, 12) = 11 THEN '项目兼职收入'
    ELSE CONCAT('MySQL 演示记录 ', n + 1)
  END,
  NOW(),
  NOW()
FROM seed_numbers
WHERE @transaction_count = 0;

DROP TEMPORARY TABLE seed_numbers;
