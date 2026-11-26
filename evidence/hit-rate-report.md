# 命中率报告（#3066 最小样品）

## 定义

- 命中：一条文本至少命中一条关键词规则（`rule_id` 非空）。
- 命中率 = 命中文本数 / 文本总数。
- **命中率不等于分类准确率**：本样品没有人工标注的“正确编码”，
  只统计规则是否命中；不声称归一化结果与人工判断一致。

## 实测结果

| 项目 | 数值 |
|---|---|
| 文本总数 | 300 条 |
| 命中文本数 | 240 条 |
| 未命中文本数（映射到 other_with_text） | 60 条 |
| 命中率 | 240 / 300 = **80.00%** |
| 验收阈值 | ≥ 70% |
| 结论 | 通过 |

复跑命令与原始输出：

```bash
python normalize_skip_reasons.py --input data/texts.txt --output output/normalized.csv
# rows=300 hits=240 hit_rate=80.00%
# output=output/normalized.csv
```

CSV 文件：`output/normalized.csv`，表头 1 行 + 数据 300 行，共 301 行。
列：`step_run_id`、`text`（原文）、`code`（映射 code）、`rule_id`（命中的 rule_id；
未命中时为空，code 为 other_with_text）。

## 按编码分布（数据行数）

| code | 行数 | code | 行数 |
|---|---|---|---|
| not_applicable | 20 | duplicate_step | 25 |
| member_declined | 20 | step_unclear | 20 |
| prerequisite_missing | 25 | system_blocked | 25 |
| staff_shortage | 25 | customer_request | 20 |
| venue_unavailable | 20 | time_conflict | 20 |
| budget_not_approved | 20 | other_with_text | 60 |

25 行的 4 个编码（prerequisite_missing、staff_shortage、duplicate_step、
system_blocked）各含 5 条双规则文本中取胜的那一方；其余命中编码各 20 行。
双规则文本共 20 条（见下）。

## 语料生成规则（全部虚构）

- 来源：`scripts/generate_texts.py` 按固定模板生成，未使用买方真实历史文本
  （我们也没有买方真实历史文本）。
- 随机种子：20261126（打乱顺序用；模板内容本身固定）。
- 构成：220 条单规则文本（11 条关键词规则各 20 条，每条恰好命中一条规则）；
  20 条双规则文本（4 对规则组合各 5 条，每条恰好命中两条规则，供 AC3 检验）；
  60 条无关键词文本（中性参观记录，不含任何规则关键词）。
- 生成器逐条校验：单规则文本必须恰好命中预期的一条规则，双规则文本必须恰好
  命中预期的两条规则，无关键词文本必须零命中；任一条不符即报错退出。
- 复现：`python scripts/generate_texts.py`（确定性输出，与提交的
  `data/texts.txt` 逐字节一致）。

## 诚实说明

- 80.00% 是**本虚构语料**上的命中率，随语料分布变化；真实历史文本上的
  命中率会不同，本样品不做任何关于真实数据表现的承诺。
- 60 条未命中文本是特意安排的中性文本，不是“模型漏检”；它们按任务要求
  映射到 other_with_text，供人工复核。
- 多规则文本共 20 条，均按 priority 取最高者（数值越小越高），
  具体案例见 `ACCEPTANCE-EVIDENCE.md` 的 AC3 一节。
