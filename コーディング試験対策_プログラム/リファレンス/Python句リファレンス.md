# Python句リファレンス

困ったときに、構文の意味と定型をすぐ引けるようにしたメモです。

---

## 1. if __name__ == "__main__":

### 何をする構文か
- そのファイルが「直接実行」されたときだけ、特定の処理を動かすためのガード。
- 他ファイルから `import` されたときは実行されない。

### 典型パターン
```python
def main():
    print("run")


if __name__ == "__main__":
    main()
```

### 使いどころ
- CLIツールとして実行する入口を作るとき
- 関数定義は再利用し、実行処理だけ分離したいとき

### 注意点
- ここに重い初期化処理を書きすぎない
- テストしやすさのため、実処理は `main()` や関数側に寄せる

---

## 2. 入力引数の取り方（argparse.ArgumentParser）

### 何をするものか
- コマンドライン引数を安全に解析する標準ライブラリ。
- `--help` の自動生成や型変換、必須チェックを行える。

### 最小形
```python
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="サンプル")
    parser.add_argument("--length", type=int, nargs=2)
    return parser.parse_args()
```

### 使いどころ
- 試験用コードで入力形式を固定したい
- 引数の不足・型不一致を自動で検出したい

### 注意点
- 問題形式が標準入力（stdin）指定なら argparse は使わない
- `required=True` を適切に付けないと、Noneチェックが必要になる


### 2-1. parser.add_argument("--length", type=int, nargs=2)

### 何をしているか
- `--length` というオプション引数を1つ定義する。
- 受け取る値は「整数2個」。

### 入力例
```bash
python mycode.py --length 7 3
```

### 取得結果のイメージ
```python
args.length == [7, 3]
```

### 使いどころ
- `N K` のような固定個数の複数値を1オプションで受けたいとき

### 注意点
- `nargs=2` なので2個未満・超過だとパースエラーになる
- `type=int` なので数値以外を渡すとエラーになる


### 2-2. type の解説

### 役割
- 受け取った文字列を指定型へ変換する。
- 変換失敗時は argparse がエラー終了する。

### よく使う型
- `type=int`: 整数へ変換
- `type=float`: 浮動小数へ変換
- `type=str`: 文字列（デフォルト）

### 例
```python
parser.add_argument("--k", type=int)
```

### 注意点
- `type=int` にすると `"10"` は通るが `"10.5"` は通らない
- 負数や値域チェックは別途バリデーションで行う


### 2-3. nargs の解説

### 役割
- 「その引数が何個の値を取るか」を指定する。

### よく使う指定
- `nargs=2`: ちょうど2個
- `nargs="+"`: 1個以上
- `nargs="*"`: 0個以上
- `nargs="?"`: 0または1個

### 例
```python
parser.add_argument("--length", type=int, nargs=2)
parser.add_argument("--arr", type=int, nargs="+")
```

### 注意点
- `nargs="+"` は最低1個必要
- 固定個数を強制したいなら整数指定（例: `nargs=2`）が安全

---

## 3. 試験での時短チェック

- 入口は `main()` + `if __name__ == "__main__":` で固定
- 引数は `argparse` で受け、型変換を自動化
- 固定個数は `nargs=2`、可変長は `nargs="+"` を第一候補
- 値域や長さ一致は別関数でバリデーション
