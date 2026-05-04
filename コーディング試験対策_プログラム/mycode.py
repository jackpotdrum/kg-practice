import argparse









def validate_input(n, k, dayly_tasks):
    errors = []

    if not (1 <= n <= 2 * 10 ** 5):
        errors.append("Nは1以上2×10^5以下の整数でなければなりません。")
    if not (1 <= k <= n):
        errors.append("Kは1以上N以下の整数でなければなりません。")
    if len(dayly_tasks) != n:
        errors.append("日ごとのタスク数のリストの長さはNと一致しなければなりません。")
    for tasks in dayly_tasks:
        if not (1 <= tasks <= 10 ** 9):
            errors.append("各日のタスク数は1以上10^9以下の整数でなければなりません。")
            break

    return errors


def parse_args():
    parser = argparse.ArgumentParser(description="最も忙しい1日の総処理時間の最小値を求める")
    parser.add_argument("--days_length", type=int, nargs=2)
    parser.add_argument("--dayly_tasks", type=int, nargs="+")
    return parser.parse_args()


def can_split_with_limit(dayly_tasks, k, limit):
    groups = 1
    current_sum = 0

    for task in dayly_tasks:
        if current_sum + task <= limit:
            current_sum += task
        else:
            groups += 1
            current_sum = task
            if groups > k:
                return False

    return True


def minimize_max_daily_load(dayly_tasks, k):
    low = max(dayly_tasks)
    high = sum(dayly_tasks)

    while low < high:
        mid = (low + high) // 2
        if can_split_with_limit(dayly_tasks, k, mid):
            high = mid
        else:
            low = mid + 1

    return low


def main():
    args = parse_args()
    if args.days_length is None or args.dayly_tasks is None:
        print("入力が不足しています。--days_length N K --dayly_tasks A1 A2 ... AN を指定してください。")
        return

    n, k = args.days_length
    dayly_tasks = args.dayly_tasks

    errors = validate_input(n, k, dayly_tasks)
    if errors:
        print("入力に誤りがあります")
        print("=========================================")
        for error in errors:
            print(error)
        return

    answer = minimize_max_daily_load(dayly_tasks, k)
    print(answer)


if __name__ == "__main__":
    main()