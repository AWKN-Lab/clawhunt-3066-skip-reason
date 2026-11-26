"""matcher 单元测试：单条匹配、字面关键词、大小写。"""

import re

from src.matcher import Rule, load_rules, match_all
from src.normalizer import normalize


def test_single_keyword_match():
    result = normalize("场馆已满，参观安排不下。")
    assert result.code == "venue_unavailable"
    assert result.rule_id == "R040"


def test_case_insensitive_latin_pattern():
    rules = [Rule(rule_id="R001", pattern="ABC|xyz", code="c", priority=1)]
    assert [m.keyword for m in match_all("xxABCyy", rules)] == ["ABC"]
    assert [m.keyword for m in match_all("xxabcyy", rules)] == ["abc"]


def test_patterns_are_literal_alternations():
    # YAML 里的 pattern 只能是字面关键词用 | 连接，不含正则通配符。
    for rule in load_rules():
        for part in rule.pattern.split("|"):
            assert re.escape(part) == part, f"{rule.rule_id} 的 pattern 含正则元字符：{part}"
