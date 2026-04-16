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

## 関連

- 逆引き: [逆引き_やりたいことからSQLを選ぶ.md](逆引き_やりたいことからSQLを選ぶ.md)
