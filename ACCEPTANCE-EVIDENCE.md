# 验收证据（#3066 最小样品）

任务 S6-SOPR-004：会员空间平台 · 跳过原因编码表与历史文本关键词归一化。
本文件逐条对照 3 条验收标准，写明文件路径、测试名与真实输出。
全部数字来自真实运行，原始日志在 `evidence/`。

## 全量测试

命令：`python -m pytest -q`（Python 3.12.3，pytest 9.2.0）
原始日志：`evidence/pytest-20261126.log`

```text
......................                                                   [100%]
22 passed in 0.53s
pytest exit=0
```

22 个测试分布：AC1 8 个、AC2 4 个、AC3 5 个、matcher 3 个、S3 接口桩 2 个。

## 一键自测 setup.sh

`setup.sh` 跑完整自测：选解释器、生成语料、生成 CSV、跑 pytest、核对 CSV 行数与命中率。
解释器选择分两条线：`PY` 按版本选（第一个 Python >= 3.11）；
`TEST_PY` 按 pytest 选（遍历候选解释器，逐个试 `python -c "import pytest"`，
第一个能过的就是测试解释器）；找不到时先建本地 venv 装依赖再重找，
仍找不到就报错退出，绝不跳过自测。任何一步失败都退出非零。
重跑日志：`evidence/selftest-setup-sh-20261126.log`（2026-11-26）——
PY=python3.12（系统 Python 3.12.3），TEST_PY=.venv/bin/python（pytest 9.2.0，
系脚本建 venv 装依赖后重找所得；两条选择线在本机上分开了）；
22 passed in 0.33s，CSV rows=300 hits=240 hit_rate=80.00%，SELFTEST: PASS，exit=0。
另有一次修正前的运行记录（3066-build/selftest-setup-sh-fail-loud-20261126.log，
不进仓）：当时脚本只有试选、无 venv 兜底，系统 Python 无 pytest，脚本报错
exit=1 而不是跳过自测——这正是本次修正要保住的行为。

## AC1：种子数据正好 12 编码、4 类别，code 唯一且小写下划线

- 种子文件：`config/reasons.yaml`（SHA256 见 MANIFEST；变异自证前后一致：
  `9fc24e6b56e82b386453ce9ee723f2fe2a7229a104481396fa3807127e109e24`）
- 迁移种子：`migrations/versions/0001_create_sop_skip_reason.py`（12 条种子，
  与 YAML 的 code、类别、顺序一一对应）
- 测试：`tests/test_ac1_seed.py`（8 个）
  - `test_exactly_12_codes`、`test_exactly_4_categories`、
    `test_expected_code_set`、`test_codes_unique_and_lowercase_underscore`、
    `test_each_code_has_meaning_trigger_scenario`、
    `test_each_code_belongs_to_exactly_one_category`、
    `test_rules_cover_11_codes_and_fallback_has_no_rule`、
    `test_priorities_unique_in_yaml`
- 结果：8 个全过。12 个编码：not_applicable、member_declined、
  prerequisite_missing、staff_shortage、venue_unavailable、budget_not_approved、
  duplicate_step、step_unclear、system_blocked、customer_request、time_conflict、
  other_with_text；4 个类别：condition_not_met、resource_shortage、process_issue、
  other。11 条关键词规则覆盖除 other_with_text 外的 11 个编码；
  other_with_text 是未命中时的兜底，无关键词规则。

## AC2：脚本跑 300 条虚构文本，CSV 300 行，命中率不低于 70%

- 脚本：`normalize_skip_reasons.py`（入口）、`src/processor.py`、`src/matcher.py`
- 语料：`data/texts.txt`（300 行，由 `scripts/generate_texts.py` 按固定模板 +
  固定种子 20261126 生成；220 条单规则 + 20 条双规则 + 60 条无关键词）
- 输出：`output/normalized.csv`（表头 1 行 + 数据 300 行，共 301 行）
- 测试：`tests/test_ac2_batch.py`（4 个）
  - `test_300_texts`、`test_csv_has_300_data_rows_and_matches_recomputed_rows`、
    `test_csv_file_has_header_plus_300_lines`、`test_hit_rate_at_least_70_percent`
- 真实运行输出：

```text
rows=300 hits=240 hit_rate=80.00%
output=output/normalized.csv
```

- 命中率：240 / 300 = **80.00%** ≥ 70%，通过。
  定义：命中 = 至少命中一条关键词规则的文本数；命中率 = 命中数 / 文本总数。
  命中率不等于分类准确率（本样品没有人工标注的“正确编码”）。
  详见 `evidence/hit-rate-report.md`（含按编码分布：60 行 other_with_text，
  其余 11 个编码各 20 或 25 行；双规则文本 20 条）。
- CSV 列：`step_run_id`、`text`（原文）、`code`（映射 code）、`rule_id`
  （命中的 rule_id；未命中时为空，code 为 other_with_text）。
  测试逐行比对提交的 CSV 与实时重算结果，一致才算过。

## AC3：多规则命中按 priority 取最高者，有单元测试覆盖

- 逻辑：`src/matcher.py` 的 `resolve()`——priority 数值越小越高；
  同 priority 按 rule_id 字典序取胜。`src/normalizer.py` 的 `normalize()` 调用它。
- 测试：`tests/test_ac3_priority.py`（5 个）
  - `test_smaller_priority_wins`：文本同时命中 R010（priority 10）与 R110（110），
    取胜者为 R010。
  - `test_multi_hit_real_case_from_corpus`：真实案例（`data/texts.txt` 内亦有此句，
    CSV 中为 SR-002）——文本“人手不够，而且预算没批，这一步先跳过。”
    同时命中 R030（staff_shortage，priority 30）与 R090（budget_not_approved，90），
    取胜者为 staff_shortage（R030）。
  - `test_tie_break_by_rule_id`：同 priority 50 的两条内存规则同时命中，
    rule_id 字典序更小者（R901）取胜。
  - `test_priority_not_file_order_reverse`：反向测试——把规则顺序倒过来，
    取胜者仍为 R030；若去掉 priority 逻辑、只按文件顺序取首个，取胜者会翻成 R090。
  - `test_no_match_falls_back_to_other_with_text`：无关键词文本映射到
    other_with_text，rule_id 为空。
- 结果：5 个全过。

### 变异自证

脚本：`scripts/mutation_check.py`；原始日志：`evidence/mutation-check-20261126.log`

- A 相：原配置全量 pytest，22 passed，exit=0。
- B 相：只改 R030 priority 30 -> 95（变异配置在临时目录，仓库内配置未动），
  跑 `tests/test_ac3_priority.py`：2 failed，3 passed，exit=1。
  变红的恰好是依赖 R030 优先级的两个断言：
  `test_multi_hit_real_case_from_corpus`（取胜者翻成 budget_not_approved）与
  `test_priority_not_file_order_reverse`。
- C 相：恢复原配置，全量 pytest，22 passed，exit=0。
- 配置 SHA256 变异前后一致：
  `9fc24e6b56e82b386453ce9ee723f2fe2a7229a104481396fa3807127e109e24`。
- 结论：MUTATION CHECK: PASS。

## Alembic 迁移（SQLite 实跑，未接真实库）

- 迁移：`migrations/versions/0001_create_sop_skip_reason.py`
  （建 `sop_skip_reason` 表 + 12 条种子），说明见 `migrations/README.md`。
- 原始日志：`evidence/alembic-20261126.log`（在 /tmp 临时目录跑的 SQLite，
  未连接任何真实数据库）
- 结果：`upgrade head` exit=0，种子行数 12，alembic_version 为 0001；
  `downgrade base` exit=0，表已删除（仅剩 alembic_version 表）。
- 本样品独立跑不需要迁移；迁移仅供落库到现有数据库时使用。

## S3-SOP：未接通（接口桩）

- 文件：`src/s3_sop_stub.py`（`put_object` / `get_object` 均抛
  `S3SOPNotConnected`，明确写明“未接通”）。
- 测试：`tests/test_s3_stub.py`（2 个），全过。
- **未完成真实 S3 集成**，本样品不做任何对象存储调用。

## SHA256 清单

- `MANIFEST`：仓内全部文件（除自身外）的 SHA256 清单。
- 核验：`sha256sum -c MANIFEST`（CI 亦跑此步），全过。

## 局限（诚实说明）

- 最小样品：只覆盖任务验收的 3 条标准；真实历史文本接入、生产库迁移、
  S3-SOP 真实集成均不在本样品范围内，须中标后另行授权与对接。
- 命中率 80.00% 是本虚构语料上的实测值，随语料分布变化；
  真实历史文本上的命中率会不同，不做承诺。
- 关键词规则是字面关键词匹配，不是语义模型；同义词、错别字、口语变体
  可能漏命中，归入 other_with_text 复核。
- CI（GitHub Actions，`.github/workflows/ci.yml`）跑 pytest 与 MANIFEST 核验；
  推送后须看 CI 结果（见建造回执）。
