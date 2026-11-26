"""批量处理：虚构文本列表 -> CSV 行 + 命中率。

命中率定义：命中 = 至少命中一条关键词规则的文本数；命中率 = 命中数 / 文本总数。
命中率不等于分类准确率：本样品没有人工标注的“正确编码”，只统计规则是否命中。
"""

from __future__ import annotations

import csv

from .matcher import load_rules
from .normalizer import normalize

CSV_FIELDS = ["step_run_id", "text", "code", "rule_id"]


def process_texts(texts: list[str], rules=None) -> list[dict]:
    """逐条归一化，返回 CSV 行（step_run_id 为 SR-001 起的顺序号）。"""
    if rules is None:
        rules = load_rules()
    rows: list[dict] = []
    for i, text in enumerate(texts, start=1):
        result = normalize(text, rules)
        rows.append(
            {
                "step_run_id": f"SR-{i:03d}",
                "text": text,
                "code": result.code,
                "rule_id": result.rule_id or "",
            }
        )
    return rows


def hit_rate(rows: list[dict]) -> tuple[int, int, float]:
    """返回（命中数，总数，命中率）。命中 = rule_id 非空的行。"""
    hits = sum(1 for row in rows if row["rule_id"])
    total = len(rows)
    return hits, total, (hits / total if total else 0.0)


def write_csv(rows: list[dict], path: str) -> None:
    """写 CSV：表头 1 行 + 数据行。"""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
