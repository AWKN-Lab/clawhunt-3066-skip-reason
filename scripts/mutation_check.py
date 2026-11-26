#!/usr/bin/env python3
"""变异自证：改一条规则的 priority -> 相关断言变红；恢复 -> 全绿。

- A 相：原配置跑全量 pytest，期望 exit 0。
- B 相：复制 config/reasons.yaml 到临时目录，只改 R030 priority 30 -> 95，
  用 SKIP_REASON_CONFIG 指向变异配置跑 tests/test_ac3_priority.py，期望 exit != 0
  （多规则真实案例的取胜者应由 staff_shortage 翻成 budget_not_approved）。
- C 相：原配置重跑全量 pytest，期望 exit 0。
- 全程不改仓库内的 reasons.yaml：前后各算一次 SHA256 并打印。
- 本脚本只打印结果；调用方把原始 stdout 存入 evidence/mutation-check-20261126.log。
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config", "reasons.yaml")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def run(cmd: list[str], env: dict | None = None) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    before = sha256(CONFIG)
    print(f"config sha256 before: {before}")

    print("=== PHASE A: 原配置全量 pytest ===")
    code_a, out_a = run([sys.executable, "-m", "pytest", "-q"])
    print(out_a, end="")
    print(f"PHASE A exit={code_a}")

    print("=== PHASE B: 变异配置（R030 priority 30 -> 95）跑 test_ac3_priority.py ===")
    with tempfile.TemporaryDirectory() as tmp:
        mutated = os.path.join(tmp, "reasons-mutated.yaml")
        with open(CONFIG, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for rule in data["rules"]:
            if rule["rule_id"] == "R030":
                rule["priority"] = 95
        with open(mutated, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
        env = dict(os.environ, SKIP_REASON_CONFIG=mutated)
        code_b, out_b = run(
            [sys.executable, "-m", "pytest", "tests/test_ac3_priority.py", "-q"],
            env=env,
        )
        print(out_b, end="")
        print(f"PHASE B exit={code_b}")
    after = sha256(CONFIG)
    print(f"config sha256 after: {after}")
    print(f"config unchanged: {before == after}")

    print("=== PHASE C: 恢复原配置，全量 pytest ===")
    code_c, out_c = run([sys.executable, "-m", "pytest", "-q"])
    print(out_c, end="")
    print(f"PHASE C exit={code_c}")

    ok = code_a == 0 and code_b != 0 and code_c == 0 and before == after
    print(f"MUTATION CHECK: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
