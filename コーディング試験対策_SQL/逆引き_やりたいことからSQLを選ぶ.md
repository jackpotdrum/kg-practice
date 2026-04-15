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

## 関連

- 句ごとの整理: [SQL句リファレンス.md](SQL句リファレンス.md)
