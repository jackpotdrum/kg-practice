# 線形DP

## 概要

配列を左から右へ1回走査し、`i` 番目までの最適値を更新する最も基本的なDP。

- `dp[i]`: 先頭から `i` まで見たときの最適値
- 遷移元は `i-1`, `i-2` など近傍が中心

## 1. どんな問題で使うか

- 1次元配列を順番に処理する
- その要素を「取る/取らない」を選ぶ
- 直前または数個前の状態だけで次が決まる

典型例:

- House Robber（隣接を同時に取れない最大和）
- 階段を登る通り数
- 最大部分和（Kadane法は線形DPの特殊形）

## 2. 代表状態

- `dp[i]`: `i` 番目までで達成できる最大値/最小値/通り数

問題によっては次の2状態に分ける。

- `take[i]`: `i` を取る場合の最適
- `skip[i]`: `i` を取らない場合の最適

## 3. 実装テンプレ（House Robber型）

```python
def solve(nums):
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]

    prev2 = nums[0]                  # dp[i-2]
    prev1 = max(nums[0], nums[1])    # dp[i-1]

    for i in range(2, len(nums)):
        cur = max(prev1, prev2 + nums[i])
        prev2, prev1 = prev1, cur

    return prev1
```

## 4. 計算量

- 時間: O(N)
- 空間: O(1) または O(N)

## 5. よくあるミス

- `i=0`, `i=1` の初期化を曖昧にする
- 遷移式を立てる前に実装して破綻する
- 「最大値DP」なのに初期値0固定で負値ケースを壊す
