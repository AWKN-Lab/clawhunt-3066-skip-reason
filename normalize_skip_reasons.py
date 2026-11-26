#!/usr/bin/env python3
"""跳过原因归一化脚本入口（#3066 交付物 normalize_skip_reasons.py）。

读入 data/texts.txt（一行一条虚构文本），按 config/reasons.yaml 的关键词规则
逐条归一化，输出 CSV（列：step_run_id、text（原文）、code（映射 code）、
rule_id（命中的 rule_id；未命中为空，code 为 other_with_text）），
并打印行数与命中率。

用法：
    python normalize_skip_reasons.py --input data/texts.txt --output output/normalized.csv
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.matcher import load_rules
from src.processor import hit_rate, process_texts, write_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="跳过原因关键词归一化（虚构文本）")
    parser.add_argument("--input", default="data/texts.txt", help="输入文本文件，一行一条")
    parser.add_argument("--output", default="output/normalized.csv", help="输出 CSV 路径")
    parser.add_argument(
        "--config", default=None, help="规则配置文件（默认 config/reasons.yaml）"
    )
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        texts = [line.strip() for line in f if line.strip()]

    rules = load_rules(args.config)
    rows = process_texts(texts, rules)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    write_csv(rows, args.output)

    hits, total, rate = hit_rate(rows)
    print(f"rows={total} hits={hits} hit_rate={rate:.2%}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
