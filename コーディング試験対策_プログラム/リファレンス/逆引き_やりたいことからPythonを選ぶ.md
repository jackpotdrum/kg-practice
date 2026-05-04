# 逆引き: やりたいことからPythonを選ぶ

困ったときに、やりたいことから最短で実装方針を決めるためのメモです。

---

## 1. スクリプトを直接実行したときだけ動かしたい

### 使うもの
- `if __name__ == "__main__":`

### 最小形
```python
def main():
    print("run")


if __name__ == "__main__":
    main()
```

### 使い分けメモ
- 再利用したい関数は `main()` の外に置く
- import時に副作用を出したくないなら必須

---

## 2. コマンドライン引数を受け取りたい

### 使うもの
- `argparse.ArgumentParser`
- `parser.add_argument(...)`

### 最小形
```python
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="sample")
    parser.add_argument("--length", type=int, nargs=2)
    return parser.parse_args()
```

### 使い分けメモ
- 引数が固定数なら `nargs=2` などの整数指定
- 配列入力なら `nargs="+"`

---

## 3. N と K のように整数を2個まとめて受けたい

### 使うもの
- `parser.add_argument("--length", type=int, nargs=2)`

### 入力例
```bash
python mycode.py --length 7 3
```

### 受け取り例
```python
args = parse_args()
n, k = args.length
```

### 使い分けメモ
- 個数が固定なら `nargs=2` が最短
- 入力不足を argparse 側で弾ける

---

## 4. 値を整数にしたい（文字列のままだと困る）

### 使うもの
- `type=int`

### 最小形
```python
parser.add_argument("--k", type=int)
```

### 使い分けメモ
- パース時に自動変換できる
- 不正入力を早期に検出できる

---

## 5. 配列のように可変長で受け取りたい

### 使うもの
- `nargs="+"`（1個以上）

### 最小形
```python
parser.add_argument("--arr", type=int, nargs="+")
```

### 入力例
```bash
python mycode.py --arr 8 1 7 3 9
```

### 使い分けメモ
- 0個も許すなら `nargs="*"`
- 1個以上を必須にするなら `nargs="+"`

---

## 6. type と nargs の早見

- `type`: 1個の値を何型へ変換するか
- `nargs`: その引数が値を何個取るか

組み合わせ例:
```python
parser.add_argument("--length", type=int, nargs=2)  # intを2個
parser.add_argument("--arr", type=int, nargs="+")  # intを1個以上
```

---

## 7. 試験本番の実行順メモ

1. `parse_args()` を先に作る
2. `type` と `nargs` で形式エラーを自動検出
3. 受け取り後に値域チェック（Nの上限など）
4. 実処理は関数化し、`main()` から呼ぶ
5. `if __name__ == "__main__":` で入口を固定
