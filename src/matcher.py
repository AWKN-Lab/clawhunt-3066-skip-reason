"""关键词规则匹配：纯函数，无外部依赖。

规则：priority 数值越小优先级越高；同 priority 按 rule_id 字典序取胜。
配置来源：config/reasons.yaml；可用环境变量 SKIP_REASON_CONFIG 覆盖路径
（变异自证用，见 scripts/mutation_check.py）。
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

import yaml

DEFAULT_CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "reasons.yaml")


def get_config_path() -> str:
    """返回当前生效的规则配置文件路径（环境变量优先）。"""
    return os.environ.get("SKIP_REASON_CONFIG") or os.path.abspath(DEFAULT_CONFIG)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    pattern: str
    code: str
    priority: int
    _regex: "re.Pattern[str]" = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_regex", re.compile(self.pattern, re.IGNORECASE))

    def matched_keyword(self, text: str) -> "str | None":
        """返回文本中命中的关键词原文，未命中返回 None。"""
        m = self._regex.search(text)
        return m.group(0) if m else None


@dataclass(frozen=True)
class Match:
    rule_id: str
    code: str
    priority: int
    keyword: str


def load_rules(config_path: str | None = None) -> list[Rule]:
    """从 YAML 载入规则并校验：rule_id 唯一、priority 为整数、pattern 可编译。"""
    path = config_path or get_config_path()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    rules = []
    seen_ids: set[str] = set()
    for item in data.get("rules", []):
        rule_id = str(item["rule_id"])
        if rule_id in seen_ids:
            raise ValueError(f"rule_id 重复：{rule_id}")
        seen_ids.add(rule_id)
        priority = item["priority"]
        if not isinstance(priority, int):
            raise ValueError(f"rule {rule_id} 的 priority 不是整数：{priority!r}")
        try:
            rules.append(
                Rule(
                    rule_id=rule_id,
                    pattern=str(item["pattern"]),
                    code=str(item["code"]),
                    priority=priority,
                )
            )
        except re.error as exc:
            raise ValueError(f"rule {rule_id} 的 pattern 编译失败：{exc}") from exc
    return rules


def match_all(text: str, rules: list[Rule]) -> list[Match]:
    """返回文本命中的全部规则（不排序、不截断）。"""
    out: list[Match] = []
    for rule in rules:
        keyword = rule.matched_keyword(text)
        if keyword is not None:
            out.append(
                Match(
                    rule_id=rule.rule_id,
                    code=rule.code,
                    priority=rule.priority,
                    keyword=keyword,
                )
            )
    return out


def resolve(matches: list[Match]) -> Match | None:
    """多规则命中取最高者：priority 数值越小越高；同 priority 按 rule_id 字典序。"""
    if not matches:
        return None
    return sorted(matches, key=lambda m: (m.priority, m.rule_id))[0]
