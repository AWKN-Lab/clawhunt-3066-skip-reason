"""AC1：种子数据正好 12 编码、4 类别，code 唯一且均为小写下划线格式。"""

import re
from collections import Counter

import yaml

from src.matcher import get_config_path

CODE_RE = re.compile(r"^[a-z][a-z0-9_]*$")

EXPECTED_CODES = {
    "not_applicable",
    "member_declined",
    "prerequisite_missing",
    "staff_shortage",
    "venue_unavailable",
    "budget_not_approved",
    "duplicate_step",
    "step_unclear",
    "system_blocked",
    "customer_request",
    "time_conflict",
    "other_with_text",
}


def _load() -> dict:
    with open(get_config_path(), encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_exactly_12_codes():
    assert len(_load()["codes"]) == 12


def test_exactly_4_categories():
    assert len(_load()["categories"]) == 4


def test_expected_code_set():
    codes = {c["code"] for c in _load()["codes"]}
    assert codes == EXPECTED_CODES


def test_codes_unique_and_lowercase_underscore():
    codes = [c["code"] for c in _load()["codes"]]
    assert len(set(codes)) == len(codes), "code 不唯一"
    for code in codes:
        assert CODE_RE.match(code), f"code 格式不对：{code}"


def test_each_code_has_meaning_trigger_scenario():
    for item in _load()["codes"]:
        for field in ("label", "meaning", "trigger", "scenario"):
            assert item[field].strip(), (item["code"], field)


def test_each_code_belongs_to_exactly_one_category():
    data = _load()
    cat_ids = {c["id"] for c in data["categories"]}
    counts = Counter(c["category"] for c in data["codes"])
    assert set(counts) == cat_ids, "类别与编码归属对不上"
    for cat_id, count in counts.items():
        assert count >= 1, f"类别 {cat_id} 下没有编码"


def test_rules_cover_11_codes_and_fallback_has_no_rule():
    data = _load()
    ruled = {r["code"] for r in data["rules"]}
    assert ruled == EXPECTED_CODES - {"other_with_text"}
    assert len(data["rules"]) == 11


def test_priorities_unique_in_yaml():
    priorities = [r["priority"] for r in _load()["rules"]]
    assert len(set(priorities)) == len(priorities), "YAML 内 priority 应各不相同"
