# 木DP

## 概要

木構造に対して、各頂点を根付き木として見た部分木の最適値を計算するDP。

- `dp[v][state]`: 頂点 `v` を根とする部分木の最適値
- DFS（再帰/スタック）で子から親へ集約する

## 1. どんな問題で使うか

- 木上で選ぶ/選ばないを決める
- 部分木ごとにスコアを集計する
- 親子制約（同時選択不可など）がある

典型例:

- 木上独立集合（親子同時選択不可）
- 最小頂点被覆
- 部分木サイズや距離和の集計

## 2. 実装テンプレ（独立集合型）

```python
def tree_dp(n, graph, values):
    # dp0[v]: v を選ばない最大値
    # dp1[v]: v を選ぶ最大値
    dp0 = [0] * n
    dp1 = [0] * n

    def dfs(v, p):
        dp1[v] = values[v]
        for nv in graph[v]:
            if nv == p:
                continue
            dfs(nv, v)
            dp0[v] += max(dp0[nv], dp1[nv])
            dp1[v] += dp0[nv]

    dfs(0, -1)
    return max(dp0[0], dp1[0])
```

## 3. 計算量

- 時間: O(N)
- 空間: O(N)

## 4. よくあるミス

- 親 `p` を除外せず無限再帰
- 葉ノード初期化漏れ
- 再帰深さ制限（Pythonは `sys.setrecursionlimit` 検討）
