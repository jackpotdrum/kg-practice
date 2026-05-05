# 集合DP（bit DP）

## 概要

部分集合をビットマスクで表し、集合ごとの最適値を持つDP。

- `mask` の bit が1なら要素を含む
- `dp[mask][last]` などで順序情報も持てる

## 1. どんな問題で使うか

- 要素数が小さい（目安 N <= 20）
- 部分集合の全探索が必要
- 巡回や順序付き訪問を最適化

典型例:

- TSP（巡回セールスマン）
- 最短ハミルトン路
- 部分集合に対する最小コスト

## 2. 実装テンプレ（TSP型）

```python
def tsp(dist):
    n = len(dist)
    INF = 10**18
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0  # 0番開始

    for mask in range(1 << n):
        for u in range(n):
            if dp[mask][u] == INF:
                continue
            if not (mask >> u) & 1:
                continue
            for v in range(n):
                if (mask >> v) & 1:
                    continue
                nmask = mask | (1 << v)
                dp[nmask][v] = min(dp[nmask][v], dp[mask][u] + dist[u][v])

    full = (1 << n) - 1
    ans = min(dp[full][u] + dist[u][0] for u in range(n))
    return ans
```

## 3. 計算量

- 代表的に O(N^2 * 2^N)
- N が少し増えるだけで急増するため、適用上限に注意

## 4. よくあるミス

- `mask` の包含判定を逆に書く
- 開始状態 `dp[1<<start][start]` の初期化ミス
- N が大きいケースに無理適用してTLE
