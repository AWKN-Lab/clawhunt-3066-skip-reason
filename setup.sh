#!/usr/bin/env bash
# #3066 最小样品一键自测（setup.sh）
#
# 解释器选择分两条线，互不干扰：
#   PY      —— 按版本选：第一个 Python >= 3.11 的候选解释器（跑脚本与 CLI 用）。
#   TEST_PY —— 按 pytest 选：遍历候选解释器，逐个试 `python -c "import pytest"`，
#              第一个能过的就是测试解释器；找不到时先建本地 venv 装依赖再重找，
#              仍找不到就报错退出，绝不跳过自测。
# 任何一步失败都退出非零；自测结果（通过数、CSV 行数、命中率）全部打印出来。
set -u
cd "$(dirname "$0")"

CANDIDATES=".venv/bin/python python3.12 python3.11 python3 python"

exists() { [ -x "$1" ] || command -v "$1" >/dev/null 2>&1; }

pick_py() {
  for c in $CANDIDATES; do
    if exists "$c"; then
      if "$c" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
        echo "$c"
        return 0
      fi
    fi
  done
  return 1
}

pick_test_py() {
  for c in $CANDIDATES; do
    if exists "$c"; then
      if "$c" -c "import pytest" 2>/dev/null; then
        echo "$c"
        return 0
      fi
    fi
  done
  return 1
}

PY="$(pick_py)" || { echo "ERROR: 未找到 Python >= 3.11 的解释器" >&2; exit 1; }
echo "PY=$PY ($("$PY" --version 2>&1))"

TEST_PY="$(pick_test_py)" || {
  echo "未找到能 import pytest 的解释器，尝试建本地 venv 并安装依赖..."
  "$PY" -m venv .venv || { echo "ERROR: 创建 venv 失败；不要跳过自测。" >&2; exit 1; }
  ./.venv/bin/pip install -r requirements.txt || { echo "ERROR: 安装依赖失败；不要跳过自测。" >&2; exit 1; }
  TEST_PY="$(pick_test_py)" || {
    echo "ERROR: 安装后仍未找到能 import pytest 的解释器；不要跳过自测。" >&2
    exit 1
  }
}
echo "TEST_PY=$TEST_PY ($("$TEST_PY" -c "import pytest; print('pytest', pytest.__version__)" 2>&1))"

echo "=== 1/4 生成语料 ==="
"$PY" scripts/generate_texts.py || { echo "ERROR: 生成语料失败" >&2; exit 1; }

echo "=== 2/4 生成 CSV ==="
"$PY" normalize_skip_reasons.py --input data/texts.txt --output output/normalized.csv || { echo "ERROR: 生成 CSV 失败" >&2; exit 1; }

echo "=== 3/4 自测 pytest ==="
"$TEST_PY" -m pytest -q || { echo "ERROR: pytest 未通过" >&2; exit 1; }

echo "=== 4/4 核对 CSV 行数与命中率 ==="
"$PY" -c "
import csv
rows = list(csv.DictReader(open('output/normalized.csv', encoding='utf-8')))
hits = sum(1 for r in rows if r['rule_id'])
assert len(rows) == 300, f'CSV 数据行应为 300，实际 {len(rows)}'
assert hits >= 210, f'命中 {hits}/300，低于 70%'
print(f'CSV rows=300 hits={hits} hit_rate={hits/300:.2%}')
" || { echo "ERROR: CSV 核对失败" >&2; exit 1; }

echo "SELFTEST: PASS"
exit 0
