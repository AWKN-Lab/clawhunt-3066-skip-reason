"""跳过原因归一化：单条文本 -> 编码 + 命中的规则。

未命中任何关键词规则时，默认映射到 other_with_text（兜底编码，rule_id 为空）。
"""

from __future__ import annotations

from dataclasses import dataclass

from .matcher import Match, load_rules, match_all, resolve

FALLBACK_CODE = "other_with_text"


@dataclass(frozen=True)
class NormalizationResult:
    code: str
    rule_id: "str | None"
    matched: list[Match]


def normalize(text: str, rules=None) -> NormalizationResult:
    """归一化一条文本。rules 为空时从默认配置载入。"""
    if rules is None:
        rules = load_rules()
    matched = match_all(text, rules)
    winner = resolve(matched)
    if winner is None:
        return NormalizationResult(code=FALLBACK_CODE, rule_id=None, matched=[])
    return NormalizationResult(code=winner.code, rule_id=winner.rule_id, matched=matched)
