# メモ

とりあえずのメモを書く場所

---



with dedup as (
    select distinct user_id, login_at
    from logins
)
select
    u.signup_at as signup_date,
    sum(u.signup_at) as cohort_size,
    sum(d.login_at + interval '1 day') as d1_retained_users,
    round(d1_retained_users / cohort_size, 4) as d1_retention_rate,
    sum(d.login_at + interval '3 day') as d3_retained_users,
    round(d3_retained_users / cohort_size, 4) as d3_retention_rate,
    sum(d.login_at + interval '7 day') as d7_retained_users,
    round(d7_retained_users / cohort_size, 4) as d7_retention_rate
from dedup as d
join users as u on d.user_id = u.user_id
where signup_date >= timestamp '2026-03-01 00:00:00'
    and signup_date < timestamp '2026-03-08 00:00:00'
group by signup_date
order by signup_date asc

- `u.signup_at::date as signup_date`にある`::date`が分からない。`d1_retained_users::numeric`には`::numeric`があって似たような書き方をしているけど、何かに関係がある？
- `distinct case when login_date = signup_date + 1 then user_id end`が分からない。sqlでcase文を書くことが出来るのかな？構文がよくわからない。そして何を意味するのかも分からない。

