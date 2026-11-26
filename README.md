# 会员空间平台 · 跳过原因编码表与历史文本关键词归一化（#3066 最小样品）

任务 S6-SOPR-004 的最小可验证样品：12 个跳过原因编码、4 个类别、
关键词规则 YAML、归一化脚本、300 条虚构文本与 CSV 输出、命中率报告、
Alembic 迁移（SQLite 验证）。

> 状态：最小样品已完成并通过全部验收（见 `ACCEPTANCE-EVIDENCE.md`）。
> 完整交付以中标和后续授权为前提。本样品不连接真实数据库，不调用真实 S3。

## 12 个编码

| code | 类别 | 含义 |
|---|---|---|
| not_applicable | 条件不满足 | 该步骤对当前会员或场景不适用 |
| member_declined | 条件不满足 | 会员明确表示不做或不需要 |
| prerequisite_missing | 条件不满足 | 前置材料或条件未齐 |
| staff_shortage | 资源不足 | 当时没有足够人员执行 |
| venue_unavailable | 资源不足 | 所需场地被占或不可用 |
| budget_not_approved | 资源不足 | 所需费用或预算尚未批准 |
| duplicate_step | 流程问题 | 该步骤已经执行过 |
| step_unclear | 流程问题 | 执行者不清楚该步骤要做什么 |
| system_blocked | 流程问题 | 系统故障导致步骤无法执行 |
| customer_request | 其他 | 应客户本人要求跳过 |
| time_conflict | 其他 | 当时的时间安排冲突 |
| other_with_text | 其他 | 未命中任何规则时的兜底 |

每编码的 label、含义、触发条件、使用场景见 `config/reasons.yaml`。

## priority 规则

- 数值越小优先级越高（system_blocked 10 最高，time_conflict 110 最低）。
- 同一文本命中多条规则时取 priority 最小者；同 priority 按 rule_id 字典序取胜。
- `other_with_text` 没有关键词规则，是未命中时的兜底映射。

## 快速开始

```bash
pip install -r requirements.txt
python -m pytest -q            # 22 passed
python scripts/generate_texts.py
python normalize_skip_reasons.py --input data/texts.txt --output output/normalized.csv
# rows=300 hits=240 hit_rate=80.00%
```

## 文件结构

```text
README.md                     本文件
ACCEPTANCE-EVIDENCE.md        逐条验收证据（文件路径、测试名、真实输出）
MANIFEST                      SHA256 清单（sha256sum -c 全过）
config/reasons.yaml           12 编码、4 类别、11 条关键词规则
src/matcher.py                关键词匹配与 priority 取胜逻辑
src/normalizer.py             单条文本归一化
src/processor.py              批量处理、CSV 写出、命中率计算
src/s3_sop_stub.py            S3-SOP 接口桩（未接通，调用即报错）
normalize_skip_reasons.py     脚本入口：虚构文本 -> CSV
scripts/generate_texts.py     生成 300 条虚构文本（种子 20261126）
scripts/mutation_check.py     变异自证：改 priority -> 断言变红，恢复 -> 全绿
migrations/                   Alembic 迁移（建表 + 12 条种子，SQLite 验证）
data/texts.txt                300 条虚构文本（一行一条）
output/normalized.csv         归一化输出：表头 1 行 + 数据 300 行
tests/                        pytest 用例（AC1/AC2/AC3 + matcher + S3 桩）
evidence/                     原始日志与命中率报告
```

## CSV 与命中率

- 列：`step_run_id`、`text`（原文）、`code`（映射 code）、`rule_id`（命中的 rule_id；
  未命中时为空，code 为 `other_with_text`）。
- 命中率定义：命中 = 至少命中一条关键词规则的文本数；命中率 = 命中数 / 文本总数。
  **命中率不等于分类准确率**（本样品没有人工标注的“正确编码”）。
- 实测：240 / 300 = **80.00%**（阈值 ≥ 70%），详见 `evidence/hit-rate-report.md`。

## 数据来源（全部虚构）

- 300 条文本由 `scripts/generate_texts.py` 按固定模板 + 固定种子 20261126 生成，
  未使用买方真实历史文本（我们也没有）。
- 命中率随语料分布变化；真实历史文本上的命中率会不同，本样品不做承诺。

## Alembic：是否需要迁移

- 本样品独立跑（配置 + CSV 处理）**不需要迁移**，不连接数据库。
- 如需落库到现有数据库，提供 `migrations/versions/0001_create_sop_skip_reason.py`
  （建 `sop_skip_reason` 表 + 12 条种子），已在 SQLite 上实跑
  upgrade/downgrade 验证通过，日志见 `evidence/alembic-20261126.log`。
  **未接真实库**，未对真实库执行过任何操作。

## S3-SOP：未接通

- 对象存储接口以 `src/s3_sop_stub.py` 的接口桩标明（`put_object` / `get_object`），
  调用即抛 `S3SOPNotConnected`。**不要宣称已完成真实 S3 集成。**

## 局限（诚实说明）

- 最小样品：只覆盖任务验收的 3 条标准；真实历史文本接入、生产库迁移、
  S3-SOP 真实集成均不在本样品范围内，须中标后另行授权与对接。
- 关键词规则是字面关键词匹配（`pattern` 为转义后的关键词用 `|` 连接），
  不是语义模型；同义词、错别字、口语变体可能漏命中，归入 other_with_text 复核。
