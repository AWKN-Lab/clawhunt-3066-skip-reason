"""AC2：脚本对 300 条虚构文本运行成功，输出 CSV 行数为 300，命中率不低于 70%。

命中率定义：命中 = 至少命中一条关键词规则的文本数；命中率 = 命中数 / 300。
命中率不等于分类准确率：本样品没有人工标注的“正确编码”，只统计规则是否命中。
"""

import csv
import os

from src.matcher import load_rules
from src.processor import CSV_FIELDS, hit_rate, process_texts

ROOT = os.path.join(os.path.dirname(__file__), "..")
TEXTS_PATH = os.path.join(ROOT, "data", "texts.txt")
CSV_PATH = os.path.join(ROOT, "output", "normalized.csv")


def _texts() -> list[str]:
    with open(TEXTS_PATH, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def test_300_texts():
    assert len(_texts()) == 300


def test_csv_has_300_data_rows_and_matches_recomputed_rows():
    rows = process_texts(_texts(), load_rules())
    assert len(rows) == 300
    # 提交的 CSV 须与实时重算逐行一致（证明 CSV 是真实跑出来的，不是手写的）。
    assert os.path.exists(CSV_PATH), "先运行 python normalize_skip_reasons.py 生成 output/normalized.csv"
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == CSV_FIELDS
        file_rows = list(reader)
    assert len(file_rows) == 300, f"CSV 数据行应为 300，实际 {len(file_rows)}"
    for a, b in zip(file_rows, rows):
        assert a == b, f"CSV 行与重算不一致：{a} vs {b}"


def test_csv_file_has_header_plus_300_lines():
    with open(CSV_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 301, f"CSV 文件应为表头 1 行 + 数据 300 行，实际 {len(lines)} 行"


def test_hit_rate_at_least_70_percent():
    rows = process_texts(_texts(), load_rules())
    hits, total, rate = hit_rate(rows)
    assert total == 300
    assert hits >= 210, f"命中 {hits}/300，低于 70%"
    assert rate >= 0.70
