import argparse

def validate_input(length, count, plan_a, plan_b):
    errors = []

    if not (1 <= length <= 2 * 10 ** 5):
        errors.append("データ件数は1以上2×10^5以下でなければなりません。")
    if not (0 <= count <= min(length - 1, 50)):
        errors.append("戦略A/Bの切り替え回数は0以上かつ\
                      データ件数-1もしくは50以下でなければなりません。")
    if not (length == len(plan_a) == len(plan_b)):
        errors.append("データ件数と戦略A/Bの利益の数は一致していなければなりません。")
    for a in plan_a:
        if not (-10 ** 9 <= a <= 10 ** 9):
            errors.append("戦略Aの利益は-10^9以上10^9以下でなければなりません。")
            break
    for b in plan_b:
        if not (-10 ** 9 <= b <= 10 ** 9):
            errors.append("戦略Bの利益は-10^9以上10^9以下でなければなりません。")
            break
    
    return errors

def parse_args():
    parser = argparse.ArgumentParser(description="戦略A/BをK回以下に抑え総利益の最大値を求める")
    parser.add_argument("--length_count", type=int, nargs=2)
    parser.add_argument("--plan_a", type=int, nargs="*")
    parser.add_argument("--plan_b", type=int, nargs="*")
    return parser.parse_args()

def gross_profit(length, count, plan_a, plan_b):
    # 切り替え無しの利益を計算
    profit_a = sum(plan_a)
    profit_b = sum(plan_b)
    no_change_profit = [profit_a, profit_b]

    if length == 1 or count == 0:
        return max(no_change_profit)
    
    # 切り替え回数が1以上の場合の利益を計算
    negative_inf = -10 ** 30

    # prev_a[c]: 前日まで見て「最後がA」で切り替え回数が c 回の最大利益
    # prev_b[c]: 前日まで見て「最後がB」で切り替え回数が c 回の最大利益
    prev_a = [negative_inf] * (count + 1)
    prev_b = [negative_inf] * (count + 1)

    # 1日目は切り替え回数0でAかBを選ぶだけ
    prev_a[0] = plan_a[0]
    prev_b[0] = plan_b[0]

    for day in range(1, length):
        cur_a = [negative_inf] * (count + 1)
        cur_b = [negative_inf] * (count + 1)

        for changes in range(count + 1):
            # 前日もAを選んで今日もA（切り替え回数は増えない）
            cur_a[changes] = prev_a[changes] + plan_a[day]
            # 前日もBを選んで今日もB（切り替え回数は増えない）
            cur_b[changes] = prev_b[changes] + plan_b[day]

            if changes > 0:
                # B -> A に切り替える
                cur_a[changes] = max(cur_a[changes], prev_b[changes - 1] + plan_a[day])
                # A -> B に切り替える
                cur_b[changes] = max(cur_b[changes], prev_a[changes - 1] + plan_b[day])

        prev_a = cur_a
        prev_b = cur_b

    return max(max(prev_a), max(prev_b))



def main():
    args = parse_args()
    length, count = args.length_count
    plan_a = args.plan_a
    plan_b = args.plan_b

    errors = validate_input(length, count, plan_a, plan_b)
    if errors:
        print("入力に誤りがあります")
        print("======================================")
        for error in errors:
            print(error)
        return
    
    result = gross_profit(length, count, plan_a, plan_b)
    print(result)

    return

if __name__ == "__main__":
    main()