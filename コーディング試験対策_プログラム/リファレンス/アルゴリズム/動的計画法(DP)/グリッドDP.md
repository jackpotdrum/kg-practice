# グリッドDP

## 概要

マス目上で移動しながら最短/最小コストや通り数を求めるDP。

- `dp[r][c]`: マス `(r, c)` に到達する最適値
- 遷移元は上や左など、移動規則で決まる

## 1. どんな問題で使うか

- 右/下移動など方向制約がある
- 障害物ありの経路数を数える
- 各マスのコスト合計を最小化する

典型例:

- ユニークパス（通り数）
- 最小経路和
- 障害物付き最短経路

## 2. 実装テンプレ（最小経路和）

```python
def min_path_sum(grid):
    h, w = len(grid), len(grid[0])
    INF = 10**18
    dp = [[INF] * w for _ in range(h)]
    dp[0][0] = grid[0][0]

    for r in range(h):
        for c in range(w):
            if r > 0:
                dp[r][c] = min(dp[r][c], dp[r - 1][c] + grid[r][c])
            if c > 0:
                dp[r][c] = min(dp[r][c], dp[r][c - 1] + grid[r][c])

    return dp[h - 1][w - 1]
```

## 3. 計算量

- 時間: O(HW)
- 空間: O(HW)（1行圧縮で O(W) へ削減可能）

## 4. よくあるミス

- 始点初期化漏れ
- 障害物セルの遷移を無効化し忘れる
- 通り数問題で mod の取り忘れ
