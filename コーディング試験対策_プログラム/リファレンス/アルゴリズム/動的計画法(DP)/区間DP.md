# 区間DP

## 概要

区間 `[l, r]` を状態にして、短い区間から長い区間へ答えを埋めるDP。

- `dp[l][r]`: 区間 `[l, r]` の最適値
- 遷移は分割点 `k` や両端の選択で定義する

## 1. どんな問題で使うか

- 連続区間をまとめて最適化する
- マージ順序や分割位置で結果が変わる
- 括弧列/回文/区間除去などを扱う

典型例:

- 行列連鎖積の最小コスト
- 区間マージ最小コスト
- 回文部分列の最長長

## 2. ループ順序

区間長 `length` を小さい順に回すのが基本。

1. `length = 1..N`
2. `l` を動かして `r = l + length - 1`
3. `dp[l][r]` を更新

## 3. 実装テンプレ（分割型）

```python
def interval_dp(cost):
    n = len(cost)
    INF = 10**18
    dp = [[0 if i == j else INF for j in range(n)] for i in range(n)]

    for length in range(2, n + 1):
        for l in range(0, n - length + 1):
            r = l + length - 1
            for k in range(l, r):
                dp[l][r] = min(dp[l][r], dp[l][k] + dp[k + 1][r] + merge_cost(l, r, cost))

    return dp[0][n - 1]
```

## 4. 計算量

- 多くは O(N^3)
- 工夫で O(N^2) まで落とせる問題もある

## 5. よくあるミス

- 区間長のループ順を間違える
- `k` の範囲を `l..r-1` にし忘れる
- `dp[l][l]` の初期値が問題定義とずれる
