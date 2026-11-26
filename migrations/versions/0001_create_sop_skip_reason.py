"""create sop_skip_reason + seed 12 codes

Revision ID: 0001
Revises:
Create Date: 2026-11-26

种子数据与 config/reasons.yaml 的 12 个编码一一对应（code、类别、顺序一致）。
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TABLE = "sop_skip_reason"

SEEDS = [
    {"code": "not_applicable", "label": "不适用", "category": "condition_not_met", "is_active": True, "sort_order": 1},
    {"code": "member_declined", "label": "会员拒绝", "category": "condition_not_met", "is_active": True, "sort_order": 2},
    {"code": "prerequisite_missing", "label": "前置缺失", "category": "condition_not_met", "is_active": True, "sort_order": 3},
    {"code": "staff_shortage", "label": "人手不足", "category": "resource_shortage", "is_active": True, "sort_order": 4},
    {"code": "venue_unavailable", "label": "场地不可用", "category": "resource_shortage", "is_active": True, "sort_order": 5},
    {"code": "budget_not_approved", "label": "预算未批", "category": "resource_shortage", "is_active": True, "sort_order": 6},
    {"code": "duplicate_step", "label": "重复步骤", "category": "process_issue", "is_active": True, "sort_order": 7},
    {"code": "step_unclear", "label": "步骤不清", "category": "process_issue", "is_active": True, "sort_order": 8},
    {"code": "system_blocked", "label": "系统阻断", "category": "process_issue", "is_active": True, "sort_order": 9},
    {"code": "customer_request", "label": "客户要求", "category": "other", "is_active": True, "sort_order": 10},
    {"code": "time_conflict", "label": "时间冲突", "category": "other", "is_active": True, "sort_order": 11},
    {"code": "other_with_text", "label": "其他（兜底）", "category": "other", "is_active": True, "sort_order": 12},
]


def upgrade() -> None:
    op.create_table(
        TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.bulk_insert(
        sa.table(
            TABLE,
            sa.column("code"),
            sa.column("label"),
            sa.column("category"),
            sa.column("is_active"),
            sa.column("sort_order"),
        ),
        SEEDS,
    )


def downgrade() -> None:
    op.drop_table(TABLE)
