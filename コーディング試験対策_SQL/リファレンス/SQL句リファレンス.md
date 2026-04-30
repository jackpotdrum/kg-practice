# SQL句リファレンス

困ったときに、句の意味と定型をすぐ引けるようにしたメモです。

---

## 1. WITH（CTE）

### 何をする句か
- 一時的な結果セットに名前を付ける
- 複雑なSQLを段階に分解して読みやすくする

### 典型パターン
```sql
WITH dedup AS (
  SELECT DISTINCT user_id, login_date
  FROM Logins
)
SELECT *
FROM dedup;
```

### 使いどころ
- 重複排除などの前処理を先に切り出したい
- 同じサブクエリを複数回使いたい
- まず中間結果を確認してから本体を書く

### 注意点
- CTEは基本的にそのSQL文の中だけで有効
- DB方言によって最適化の挙動が異なる

---

## 2. INTERVAL（日時の加減算）

### 何をする句か
- 日付・時刻に対して期間を足し引きする

### 典型パターン（PostgreSQL）
```sql
SELECT login_date + INTERVAL '1 day' AS next_day
FROM Logins;
```

### MySQLでの書き方
```sql
SELECT DATE_ADD(login_date, INTERVAL 1 DAY) AS next_day
FROM Logins;
```

```sql
SELECT DATE_SUB(login_date, INTERVAL 7 DAY) AS seven_days_ago
FROM Logins;
```

### PostgreSQLからMySQLへの置き換え早見
- `x + INTERVAL '1 day'` -> `DATE_ADD(x, INTERVAL 1 DAY)`
- `x - INTERVAL '7 day'` -> `DATE_SUB(x, INTERVAL 7 DAY)`
- `x + INTERVAL '2 hour'` -> `DATE_ADD(x, INTERVAL 2 HOUR)`

### 使いどころ
- 連続日判定（+1 day, +2 day）
- 期間条件（直近7日など）

### 注意点
- 方言差が大きい（MySQL, SQL Serverで書き方が違う）
- MySQLは `INTERVAL 数値 単位` の順で書く（例: `INTERVAL 1 DAY`）
- PostgreSQLは文字列型で書くことが多い（例: `INTERVAL '1 day'`）

---

## 3. EXISTS（存在チェック）

### 何をする句か
- 相関サブクエリの結果が1行でもあれば真

### 典型パターン
```sql
SELECT d.user_id, d.login_date
FROM dedup d
WHERE EXISTS (
  SELECT 1
  FROM dedup d2
  WHERE d2.user_id = d.user_id
    AND d2.login_date = d.login_date + INTERVAL '1 day'
);
```

### 使いどころ
- ある条件を満たす行が存在するかだけ知りたい
- 親子関係の有無を判定したい

### 注意点
- サブクエリは条件に一致した時点で打ち切られやすく、実務で使いやすい
- NULLの罠を避けやすい

---

## 4. IN（集合に含まれるか）

### 何をする句か
- 値がリストまたはサブクエリ結果の集合に含まれるかを判定

### 典型パターン
```sql
SELECT user_id
FROM Users
WHERE user_id IN (101, 102, 103);
```

```sql
SELECT user_id
FROM Users
WHERE user_id IN (
  SELECT user_id
  FROM VIPUsers
);
```

### 使いどころ
- 候補値の集合が明確なとき
- 1列同士の単純な集合比較をしたいとき

### 注意点
- NOT IN はサブクエリ側にNULLが混ざると意図しない結果になりやすい
- 複数列比較や複雑条件では EXISTS の方が読みやすいことが多い

---

## 5. EXISTS と IN の使い分け

### 先に結論
- 存在判定が目的なら EXISTS
- 単純な集合一致なら IN

### 判断の目安
- EXISTS を優先:
  - 相関条件がある
  - 存在有無だけ分かればよい
  - NULLの影響を避けたい
- IN を優先:
  - 小さめの固定リストで判定したい
  - 1列の集合比較を簡潔に書きたい

### 同等に書ける例
```sql
-- IN
SELECT u.user_id
FROM Users u
WHERE u.user_id IN (
  SELECT l.user_id
  FROM Logins l
);

-- EXISTS
SELECT u.user_id
FROM Users u
WHERE EXISTS (
  SELECT 1
  FROM Logins l
  WHERE l.user_id = u.user_id
);
```

---

## 6. 試験での時短チェック

- まず前処理が必要か（重複排除、日付正規化）を決める
- 連続判定は + INTERVAL の条件を1つずつ作る
- 存在判定は EXISTS を第一候補にする
- 出力列名と並び順を最後に固定する

---

## 7. WHERE と HAVING の使い分け

### 先に結論
- 行の条件は WHERE
- 集計結果（グループ）の条件は HAVING

### 処理順イメージ
1. `FROM`
2. `WHERE`（集計前の行を絞る）
3. `GROUP BY`（グループ化）
4. `HAVING`（集計後のグループを絞る）
5. `SELECT`
6. `ORDER BY`

### 典型パターン
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

### よくあるミス
- `WHERE SUM(amount) >= 50000` と書く（集計前なので不可）
- 全体合計のサブクエリで判定してしまい、顧客ごとの条件になっていない
- `GROUP BY` の列名スペルミス（例: `costomer_id`）

---

## 8. PARTITION BY（行を残したままグループ内計算）

### 何をする句か
- ウィンドウ関数の計算単位を「グループごと」に分ける
- ただし `GROUP BY` と違って、元の各行は消えない

### 先に結論
- `GROUP BY`: グループごとに集約し、行数が減る
- `PARTITION BY`: グループごとに計算するが、行数はそのまま

### 典型パターン（カテゴリごとの順位）
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

### 典型パターン（ユーザーごとの累積）
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

### GROUP BY との違い（最重要）
- `GROUP BY` は1グループ1行にまとめる（明細は消える）
- `PARTITION BY` は明細を残したまま、順位・累積・前日比較などを計算できる
- 試験のTop-N per groupは、まず集計してから `ROW_NUMBER() OVER (PARTITION BY ...)` を付ける形が定番

### よくあるミス
- `PARTITION BY` を忘れて全体順位になってしまう
- 同点時ルールを `ORDER BY` に書かず、結果が不安定になる
- `ROW_NUMBER()` の別名を同じSELECTの `WHERE` で直接使ってしまう（CTE/サブクエリで包む）

---

## 9. 型キャスト（`::date`, `::numeric`）

### 何をする句か
- 値を別の型として扱う（型変換）
- PostgreSQLでは `式::型` の形で書ける

### 典型パターン
```sql
SELECT
  signup_at::date AS signup_date,
  ROUND(d1_retained_users::numeric / cohort_size, 4) AS d1_retention_rate
FROM retention_daily;
```

### 使いどころ
- `timestamp` から日付だけ取り出して日次集計したい
- 整数同士の割り算で小数を落とさず率を計算したい

### 注意点
- `::date` は時分秒を落とす
- 率計算はどこかで `numeric` にしておく（例: `x::numeric / y`）

---

## 10. CASE式（条件分岐）

### 何をする句か
- 条件に応じて返す値を切り替える

### 基本構文
```sql
CASE
  WHEN 条件 THEN 値
  WHEN 条件 THEN 値
  ELSE 値
END
```

### 典型パターン（条件付きユニーク人数）
```sql
COUNT(DISTINCT CASE
  WHEN login_date = signup_date + 1 THEN user_id
END) AS d1_retained_users
```

### 何が起きているか
- 条件を満たす行だけ `user_id` を返す
- 条件を満たさない行は `NULL`（`ELSE` 省略時）
- `COUNT` は `NULL` を数えないため、条件一致した人数だけ数えられる
- `DISTINCT` で同一ユーザーの重複を除外できる

### 注意点
- `DISTINCT CASE WHEN ...` は単体より `COUNT(DISTINCT CASE WHEN ... END)` で使うのが定番

---

## 11. `date + 1` と `INTERVAL` の使い分け（PostgreSQL）

### 先に結論
- `date` 型同士の比較なら `signup_date + 1` でOK（1日は整数加算）
- `timestamp` に時間単位を足すなら `INTERVAL` を使う

### 例
```sql
-- date同士
login_date = signup_date + 1

-- timestamp
signup_at + INTERVAL '1 day'
```

### なぜ `+ 1` が許されるか
- PostgreSQLに `date + integer` 演算子があり、整数は日数として解釈されるため

### 注意点
- 他DBでは同じ書き方がそのまま使えないことがある（方言差）
- 比較前に型を揃えるとバグを減らせる（例: `login_at::date`, `signup_at::date`）

---

## 12. JOIN と LEFT JOIN の違い

### 先に結論
- `JOIN`（`INNER JOIN`）: 両テーブルで一致した行だけ残る
- `LEFT JOIN`: 左テーブルの行は全件残り、一致しない右側は `NULL` になる

### 典型パターン
```sql
-- INNER JOIN
SELECT u.user_id, l.login_date
FROM users u
JOIN logins l
  ON l.user_id = u.user_id;

-- LEFT JOIN
SELECT u.user_id, l.login_date
FROM users u
LEFT JOIN logins l
  ON l.user_id = u.user_id;
```

### 使い分けメモ
- 左側の母集団を絶対に欠損させたくない: `LEFT JOIN`
- 一致レコードだけ欲しい: `JOIN`（`INNER JOIN`）
- コホート分析や未ログインユーザーを含む集計は `LEFT JOIN` が基本

### 注意点
- `LEFT JOIN` の右テーブル条件を `WHERE` に書くと、実質 `INNER JOIN` になることがある
- 右テーブル条件は必要に応じて `ON` 側へ置く

---

## 13. MIN / MAX（最小値・最大値の集約）

### 何をする句か
- `MIN(列)` はグループ内の最小値を返す
- `MAX(列)` はグループ内の最大値を返す
- `GROUP BY` と組み合わせると「単位ごとの最小/最大」を取れる

### 典型パターン（ユーザー×カテゴリの最初/最新注文日時）
```sql
SELECT
  oi.category_id,
  o.user_id,
  MIN(o.ordered_at) AS first_order_at,
  MAX(o.ordered_at) AS latest_order_at
FROM orders o
JOIN order_items oi
  ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY
  oi.category_id,
  o.user_id;
```

### 使いどころ
- 「最初の日付」「最新の日付」など、値そのものが欲しいとき
- 件数や合計と同じ粒度で一緒に集約したいとき

### 注意点
- `MIN` / `MAX` は値を返すだけで、行全体は返さない
- 「最新行の別カラム（例: 最新注文の単価）も欲しい」場合は、`ROW_NUMBER()` などで最新行を特定する
- どの単位で最小/最大を取るかは `GROUP BY` の列で決まる

### 補足（今回の模擬試験との対応）
- `latest_order_at` は `MAX(ordered_at)` で取得できる
- `order_count`, `total_amount`, `latest_order_at` を同じ `GROUP BY (category_id, user_id)` で作ると、粒度が揃って堅牢になりやすい

---

## 関連

- 逆引き: [逆引き_やりたいことからSQLを選ぶ.md](逆引き_やりたいことからSQLを選ぶ.md)
