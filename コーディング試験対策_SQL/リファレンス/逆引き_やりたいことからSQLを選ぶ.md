# 逆引き: やりたいことからSQLを選ぶ

困ったときに、やりたいことから最短で方針を決めるためのメモです。

---

## 1. 一時的にテーブルを作って分解したい

### 使うもの
- WITH（CTE）

### 最小形
```sql
WITH tmp AS (
  SELECT ...
)
SELECT ...
FROM tmp;
```

### 使い分けメモ
- 前処理を分離したいときはCTEが最優先
- 同じ中間結果を複数回使う時にも有効

---

## 2. 日付の連続や期間を判定したい

### 使うもの
- INTERVAL
- EXISTS（またはJOIN）

### 最小形（3日連続）
```sql
WITH dedup AS (
  SELECT DISTINCT user_id, login_date
  FROM Logins
)
SELECT d.user_id, d.login_date AS streak_start
FROM dedup d
WHERE EXISTS (
  SELECT 1
  FROM dedup d2
  WHERE d2.user_id = d.user_id
    AND d2.login_date = d.login_date + INTERVAL '1 day'
)
AND EXISTS (
  SELECT 1
  FROM dedup d3
  WHERE d3.user_id = d.user_id
    AND d3.login_date = d.login_date + INTERVAL '2 day'
);
```

### MySQL版（同じ意味）
```sql
WITH dedup AS (
  SELECT DISTINCT user_id, login_date
  FROM Logins
)
SELECT d.user_id, d.login_date AS streak_start
FROM dedup d
WHERE EXISTS (
  SELECT 1
  FROM dedup d2
  WHERE d2.user_id = d.user_id
    AND d2.login_date = DATE_ADD(d.login_date, INTERVAL 1 DAY)
)
AND EXISTS (
  SELECT 1
  FROM dedup d3
  WHERE d3.user_id = d.user_id
    AND d3.login_date = DATE_ADD(d.login_date, INTERVAL 2 DAY)
);
```

### 使い分けメモ
- 連続判定は「同日重複の排除」を先にやる
- まず3日連続を作ってから4日以上へ拡張する
- PostgreSQLからMySQLへ移すときは、`+ INTERVAL 'n day'` を `DATE_ADD(..., INTERVAL n DAY)` に置き換える

---

## 3. 条件を満たす行が存在するかだけ知りたい

### 使うもの
- EXISTS

### 最小形
```sql
SELECT u.user_id
FROM Users u
WHERE EXISTS (
  SELECT 1
  FROM Orders o
  WHERE o.user_id = u.user_id
);
```

### 使い分けメモ
- 相関条件がある存在判定は EXISTS が自然
- 結果列を取りたいならJOINへ切り替える

---

## 4. 候補集合に含まれるか判定したい

### 使うもの
- IN

### 最小形
```sql
SELECT user_id
FROM Users
WHERE user_id IN (101, 102, 103);
```

### 使い分けメモ
- 固定値リストならINが最短
- サブクエリでNULLが混ざる可能性があるなら EXISTS を検討

---

## 5. EXISTS と IN で迷ったとき

### 3秒ルール
- 存在チェックが目的: EXISTS
- 値集合への所属判定: IN

### 追加判断
- NOT IN はNULLの影響を受けやすいので要注意
- 複雑条件や相関サブクエリなら EXISTS が読みやすい

---

## 6. 試験本番の実行順メモ

1. 出力列と並び順を先に固定
2. 前処理が必要ならWITHを作る
3. 判定ロジックをEXISTS/INで組む
4. 日付条件をINTERVALで足す
5. サンプル2〜3件で手計算検証する

---

## 7. 期間を指定してデータを取得したい

### 使うもの
- WHERE
- 比較演算子（`>=`, `<`）

### 最小形（開始日以上・終了日未満）
```sql
SELECT *
FROM sales
WHERE order_date >= '2026-03-01'
  AND order_date < '2026-04-01';
```

### 今回の3月データ例（顧客ごと集計つき）
```sql
SELECT
  customer_id,
  SUM(amount) AS total_amount
FROM sales
WHERE order_date >= '2026-03-01'
  AND order_date < '2026-04-01'
GROUP BY customer_id
HAVING SUM(amount) >= 50000
ORDER BY total_amount DESC;
```

### 使い分けメモ
- 日付の期間抽出は `BETWEEN` よりも「`>= 開始` かつ `< 終了`」が安全
- `DATETIME` 型でも月末23:59:59問題を避けやすい
- 期間条件は `WHERE`、集計条件は `HAVING`

---

## 8. グループごとに計算したいが、元の各行は残したい

### 使うもの
- PARTITION BY（ウィンドウ関数）
- ROW_NUMBER / RANK / DENSE_RANK / SUM OVER など

### 最小形（カテゴリごと順位）
```sql
SELECT
  category,
  product_id,
  total_sales,
  ROW_NUMBER() OVER (
    PARTITION BY category
    ORDER BY total_sales DESC, product_id ASC
  ) AS rank_in_category
FROM product_sales;
```

### 最小形（ユーザーごとの累積）
```sql
SELECT
  user_id,
  purchased_at,
  amount,
  SUM(amount) OVER (
    PARTITION BY user_id
    ORDER BY purchased_at
  ) AS running_amount
FROM purchases;
```

### GROUP BY との違い
- `GROUP BY`: 1グループ1行に集約（行数が減る）
- `PARTITION BY`: 行数を減らさず、グループ内で順位や累積を計算

### 使い分けメモ
- 明細を残したまま「グループ内Top-N」や「累積」を出すなら `PARTITION BY`
- 集計結果だけ欲しいなら `GROUP BY`
- Top-N per group の定番は「集計CTE -> `ROW_NUMBER() OVER (PARTITION BY ...)` -> `rank <= N`」

---

## 9. `timestamp` を日付にしたい / 割り算を小数で計算したい

### 使うもの
- 型キャスト（PostgreSQLの `::`）

### 最小形
```sql
SELECT
  signup_at::date AS signup_date,
  ROUND(retained_users::numeric / cohort_size, 4) AS retention_rate
FROM retention_daily;
```

### 使い分けメモ
- 日単位で比較・集計したいなら `::date`
- 率計算で小数を落としたくないなら `::numeric`

---

## 10. 条件を満たすユーザー数だけ数えたい（重複は除外したい）

### 使うもの
- CASE
- COUNT(DISTINCT ...)

### 最小形
```sql
COUNT(DISTINCT CASE
  WHEN login_date = signup_date + 1 THEN user_id
END) AS d1_retained_users
```

### 使い分けメモ
- `CASE WHEN` で条件一致時のみ `user_id` を返す
- 条件不一致は `NULL` になる
- `COUNT` は `NULL` を数えない
- `DISTINCT` で同一ユーザー重複を除外できる

---

## 11. 日付の「翌日」を書きたい（`+ 1` と `INTERVAL` のどちら？）

### 使うもの
- `date + integer`
- `INTERVAL`

### 最小形
```sql
-- date同士の比較
login_date = signup_date + 1

-- timestampに加算
signup_at + INTERVAL '1 day'
```

### 使い分けメモ
- `date` 型なら `+ 1` は1日加算として使える（PostgreSQL）
- `timestamp` 型や時間単位を扱うなら `INTERVAL` を使う
- 比較前に `::date` で型を揃えると安全

---

## 12. 左側の母集団を落とさずに結合したい（未ログインも含めたい）

### 使うもの
- LEFT JOIN

### 最小形
```sql
SELECT
  u.user_id,
  l.login_date
FROM users u
LEFT JOIN logins l
  ON l.user_id = u.user_id;
```

### JOIN との違い
- `JOIN`（`INNER JOIN`）: 一致した行だけ残る
- `LEFT JOIN`: 左テーブルは全件残る（一致しない右側は `NULL`）

### 使い分けメモ
- コホートの分母を正しく保持したい: `LEFT JOIN`
- 一致レコードだけ見たい: `JOIN`
- 「未ログインも含む集計」は `LEFT JOIN` を第一候補にする

### 注意点
- `LEFT JOIN` 後に右テーブル列を `WHERE` で絞りすぎると、未一致行が落ちる
- 右テーブル条件は必要に応じて `ON` 側へ置く

---

## 13. グループごとの最新日・最古日を取りたい

### 使うもの
- MAX（最新値）
- MIN（最古値）
- GROUP BY

### 最小形
```sql
SELECT
  category_id,
  user_id,
  MIN(ordered_at) AS first_order_at,
  MAX(ordered_at) AS latest_order_at
FROM user_category_orders
GROUP BY category_id, user_id;
```

### 使い分けメモ
- 日付や数値の「最大/最小の値そのもの」が欲しいだけなら `MIN` / `MAX` が最短
- 件数・合計と同時に出したい場合も、同じ `GROUP BY` でまとめて作ると安全
- 例: `order_count`, `total_amount`, `latest_order_at` を1つの集約CTEで作る

### ここが境界（`MIN` / `MAX` では足りないケース）
- 「最新行の他の列」も欲しいとき（例: 最新注文の `unit_price`）
- この場合は `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ordered_at DESC)` で最新行を特定する

---

## 関連

- 句ごとの整理: [SQL句リファレンス.md](SQL句リファレンス.md)
