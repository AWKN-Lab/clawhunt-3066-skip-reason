"""AC3：同一文本命中多条规则时按 priority 取最高者，有单元测试覆盖。

priority 规则：数值越小优先级越高；同 priority 按 rule_id 字典序取胜。
含反向测试：去掉 priority 逻辑（只按文件顺序取首个）时，取胜者会翻掉。
"""

from src.matcher import Rule, load_rules, match_all, resolve
from src.normalizer import normalize


def test_smaller_priority_wins():
    rules = load_rules()
    text = "系统卡住了，今天也没时间，只能跳过。"
    matched = match_all(text, rules)
    assert {m.rule_id for m in matched} == {"R010", "R110"}
    assert resolve(matched).rule_id == "R010"  # priority 10 < 110


def test_multi_hit_real_case_from_corpus():
    # 证据中的真实案例（data/texts.txt 内亦有此句，见 output/normalized.csv）：
    # 同时命中 R030（staff_shortage，priority 30）与 R090（budget_not_approved，90）。
    text = "人手不够，而且预算没批，这一步先跳过。"
    result = normalize(text)
    assert result.code == "staff_shortage"
    assert result.rule_id == "R030"
    assert {m.rule_id for m in result.matched} == {"R030", "R090"}


def test_tie_break_by_rule_id():
    # 同 priority 时按 rule_id 字典序取胜（内存构造的规则集，YAML 内无重复 priority）。
    rules = [
        Rule(rule_id="R902", pattern="甲", code="code_b", priority=50),
        Rule(rule_id="R901", pattern="甲", code="code_a", priority=50),
    ]
    matched = match_all("甲", rules)
    assert len(matched) == 2
    assert resolve(matched).rule_id == "R901"


def test_priority_not_file_order_reverse():
    # 反向测试：把规则顺序倒过来，取胜者不变；
    # 若去掉 priority 逻辑、只按文件顺序取首个，取胜者会翻掉。
    rules = load_rules()
    text = "人手不够，而且预算没批，这一步先跳过。"
    forward = resolve(match_all(text, rules))
    reversed_rules = list(reversed(rules))
    backward = resolve(match_all(text, reversed_rules))
    assert forward.rule_id == backward.rule_id == "R030"
    assert match_all(text, rules)[0].rule_id == "R030"
    assert match_all(text, reversed_rules)[0].rule_id == "R090"


def test_no_match_falls_back_to_other_with_text():
    result = normalize("今天带客户参观了开放工位，整体感觉不错。")
    assert result.code == "other_with_text"
    assert result.rule_id is None
    assert result.matched == []
