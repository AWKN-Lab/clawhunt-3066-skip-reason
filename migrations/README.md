# migrations 说明

本样品独立跑（配置 + CSV 处理）**不需要迁移**：归一化脚本只读写本地文件，
不连接数据库。是否需要迁移，取决于买方现有系统是否要把编码表落库：

- 如果编码表只作为独立配置文件 + CSV 处理使用，不需要迁移。
- 如果要进入现有数据库，用本目录的 migration（`versions/0001_create_sop_skip_reason.py`）：
  建 `sop_skip_reason` 表（code 唯一）并插入 12 条种子数据，与
  `config/reasons.yaml` 的 12 个编码一一对应。

验证方式（仅 SQLite，未接真实库）：

```bash
cp -r migrations /tmp/alembic-check-20261126
cd /tmp/alembic-check-20261126
export ALEMBIC_SQL_URL=sqlite:////tmp/alembic-check-20261126/test.db
alembic -c migrations/alembic.ini upgrade head   # 建表 + 12 条种子
alembic -c migrations/alembic.ini downgrade base # 删表
```

验证日志见 `evidence/alembic-20261126.log`。
