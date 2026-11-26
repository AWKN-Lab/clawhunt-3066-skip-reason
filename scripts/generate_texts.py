#!/usr/bin/env python3
"""生成 300 条虚构文本（data/texts.txt），供 #3066 最小样品使用。

语料来源：全部虚构，由本脚本按固定模板 + 固定随机种子生成；
未使用买方真实历史文本（我们也没有）。
生成规则（随机种子 20261126）：
- 220 条单规则文本：11 条关键词规则各 20 条，每条恰好命中一条规则；
- 20 条双规则文本：4 对规则组合各 5 条，每条恰好命中两条规则（供 AC3 检验）；
- 60 条无关键词文本：中性参观记录，不含任何规则关键词。
生成后逐条用 matcher 校验命中情况，任一条不符预期即报错退出；
最后按种子打乱顺序写入 data/texts.txt（一行一条）。
预期命中率：240 / 300 = 80.00%（命中 = 至少命中一条关键词规则）。
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.matcher import load_rules, match_all

SEED = 20261126

SINGLE_TEMPLATES: dict[str, list[str]] = {
    "R010": [
        "系统卡住了，参观登记这一步只能先跳过。",
        "系统故障，今天没法在系统里登记。",
        "系统报错，提交按钮点不了。",
        "页面打不开，登记步骤做不了。",
        "系统卡住好几次了，这一步先跳过吧。",
        "系统故障导致无法录入，只能跳过。",
    ],
    "R020": [
        "缺少前置材料，这一步做不了。",
        "前置条件不满足，先跳过。",
        "资料不全，等补齐了再做。",
        "缺少材料，暂时跳过这一步。",
        "前置条件不满足，需要先补资料。",
        "资料不全，无法继续。",
    ],
    "R030": [
        "今天人手不够，带参观这一步先跳过。",
        "现在没人能带，只能跳过。",
        "人员不足，接待不过来。",
        "排不上人，这一步先不做了。",
        "人手不够，只能下次再安排。",
        "现场没人，这一步跳过。",
    ],
    "R040": [
        "场地被占了，今天用不了。",
        "没有场地，这一步先跳过。",
        "场地不可用，下次再约。",
        "场馆已满，参观安排不下。",
        "场地被占，只能先跳过。",
        "没有场地可用，跳过这一步。",
    ],
    "R050": [
        "这一步已经做过了，不用再做。",
        "重复步骤，跳过。",
        "刚才已经做过了，这一步重复了。",
        "这一步和前面重复了，跳过。",
        "已经做过了，不用重复。",
        "重复步骤，直接跳过。",
    ],
    "R060": [
        "会员拒绝了这一步。",
        "客户说不需要，直接跳过。",
        "会员说不用了，这一步跳过。",
        "他不想做这一步。",
        "会员拒绝参观洽谈室。",
        "客户说不需要介绍，直接跳过。",
    ],
    "R070": [
        "这一步不适用，跳过。",
        "会员说与我无关，不用做。",
        "不符合条件，这一步不适用。",
        "这个步骤对他不适用。",
        "不符合条件，跳过这一步。",
        "与我无关，跳过。",
    ],
    "R080": [
        "步骤不清楚，不知道怎么操作。",
        "不知道怎么做这一步，先跳过。",
        "看不懂步骤，只能先放一放。",
        "步骤不清楚，需要有人教一下。",
        "这一步看不懂步骤，跳过。",
        "不知道怎么做，先跳过。",
    ],
    "R090": [
        "预算没批，这一步先不做。",
        "预算未批准，等批了再说。",
        "费用没批下来，跳过这一步。",
        "没预算，活动先暂停。",
        "预算没批下来，只能跳过。",
        "预算未批准，这一步做不了。",
    ],
    "R100": [
        "客户要求跳过这一步。",
        "客户提出先不做洽谈室参观。",
        "客人要求直接看独立办公室。",
        "客户要求下次再来。",
        "客户提出跳过登记环节。",
        "客人要求跳过这一步。",
    ],
    "R110": [
        "时间冲突，只能改天。",
        "时间对不上，这一步先跳过。",
        "今天没时间，改天再来。",
        "时间冲突，参观改到下周。",
        "没时间了，这一步跳过。",
        "时间对不上，只能改约。",
    ],
}

# 双规则文本：每对恰好命中两条规则（第一条 priority 更小，应取胜）。
PAIR_TEMPLATES: list[tuple[str, str, list[str]]] = [
    (
        "R030",
        "R090",
        [
            "人手不够，而且预算没批，这一步先跳过。",
            "排不上人，预算没批，只能先不做。",
            "人员不足，费用没批下来，跳过这一步。",
            "现场没人，预算未批准，这一步做不了。",
            "人手不够，预算没批下来，只能下次。",
        ],
    ),
    (
        "R010",
        "R110",
        [
            "系统卡住了，今天也没时间，只能跳过。",
            "系统故障，时间对不上，这一步先不做。",
            "页面打不开，没时间了，跳过这一步。",
            "系统报错，时间冲突，参观改到下周。",
            "系统卡住好几次了，时间对不上，只能改约。",
        ],
    ),
    (
        "R020",
        "R040",
        [
            "缺少前置材料，场地被占了，这一步做不了。",
            "资料不全，场馆已满，跳过这一步。",
            "前置条件不满足，没有场地，先跳过。",
            "缺少材料，场地不可用，下次再约。",
            "资料不全，场地被占，只能先跳过。",
        ],
    ),
    (
        "R050",
        "R060",
        [
            "这一步已经做过了，会员也说不需要。",
            "重复步骤，客户说不用了，直接跳过。",
            "刚才已经做过了，他不想再做一遍。",
            "这一步和前面重复了，会员拒绝再做。",
            "已经做过了，客户说不需要介绍，直接跳过。",
        ],
    ),
]

NEUTRAL_TEMPLATES: list[str] = [
    "今天带客户参观了开放工位，整体感觉不错。",
    "会员对共享空间的采光很满意。",
    "洽谈室的桌椅已经摆放整齐。",
    "前台接待流程今天很顺畅。",
    "客户问了会员价格，正在考虑。",
    "下午有一场小型分享会，正在准备。",
    "独立办公室的钥匙已经交给客户了。",
    "参观结束后客户在洽谈室坐了一会儿。",
    "今天的参观路线走了三遍，都很顺利。",
    "会员对共享空间的咖啡表示满意。",
    "前台今天收到两份新的参观预约。",
    "洽谈室的投影仪已经调试好了。",
]


def main() -> int:
    rules = load_rules()
    by_id = {r.rule_id: r for r in rules}

    singles: list[tuple[str, str]] = []  # (text, expected rule_id)
    for rule_id, templates in SINGLE_TEMPLATES.items():
        for i in range(20):
            singles.append((templates[i % len(templates)], rule_id))

    pairs: list[tuple[str, tuple[str, str]]] = []
    for first, second, templates in PAIR_TEMPLATES:
        for template in templates:
            pairs.append((template, (first, second)))

    neutrals: list[str] = [NEUTRAL_TEMPLATES[i % len(NEUTRAL_TEMPLATES)] for i in range(60)]

    # 逐条校验命中情况，不符预期即报错。
    for text, expected in singles:
        matched = match_all(text, rules)
        got = [m.rule_id for m in matched]
        if got != [expected]:
            print(f"单规则文本校验失败：{text!r} 期望 [{expected}] 实际 {got}")
            return 1
    for text, (first, second) in pairs:
        matched = match_all(text, rules)
        got = sorted(m.rule_id for m in matched)
        if got != sorted([first, second]):
            print(f"双规则文本校验失败：{text!r} 期望 {sorted([first, second])} 实际 {got}")
            return 1
    for text in neutrals:
        matched = match_all(text, rules)
        if matched:
            print(f"无关键词文本校验失败：{text!r} 意外命中 {[m.rule_id for m in matched]}")
            return 1

    all_texts = (
        [t for t, _ in singles] + [t for t, _ in pairs] + neutrals
    )
    assert len(all_texts) == 300, len(all_texts)
    rng = random.Random(SEED)
    rng.shuffle(all_texts)

    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "texts.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_texts) + "\n")
    hits = len(singles) + len(pairs)
    print(f"texts=300 singles={len(singles)} pairs={len(pairs)} neutral={len(neutrals)}")
    print(f"expected hits={hits} hit_rate={hits / 300:.2%} seed={SEED}")
    print(f"output={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
