# 文字列DP

## 概要

2つ（または1つ）の文字列に対して、部分一致・編集・変換コストを求めるDP。

- `dp[i][j]`: 文字列Aの先頭i文字とBの先頭j文字までの最適値

## 1. どんな問題で使うか

- 最長共通部分列（LCS）
- 編集距離（挿入・削除・置換）
- 部分文字列の一致判定

## 2. LCS テンプレ

```python
def lcs_length(s, t):
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[n][m]
```

## 3. 編集距離の遷移

- 挿入: `dp[i][j-1] + 1`
- 削除: `dp[i-1][j] + 1`
- 置換: `dp[i-1][j-1] + cost`

## 4. 計算量

- 時間: O(NM)
- 空間: O(NM)（行圧縮で O(min(N, M)) まで削減可能）

## 5. よくあるミス

- 1-index と 0-index の対応を崩す
- `dp[0][*]`, `dp[*][0]` の初期化忘れ
- 問題が「部分列」か「部分文字列」かを取り違える
