"""initial

Revision ID: 0001
Revises: 
Create Date: 2024-10-05 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "listings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("listing_id", sa.String(length=64), nullable=False, unique=True, index=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("dealer_name", sa.String(length=128)),
        sa.Column("dealer_group", sa.String(length=128)),
        sa.Column("dealer_city", sa.String(length=64)),
        sa.Column("dealer_state", sa.String(length=2)),
        sa.Column("phone", sa.String(length=32)),
        sa.Column("dealer_vdp_url", sa.Text, nullable=False),
        sa.Column("aggregator_url", sa.Text),
        sa.Column("stock_no", sa.String(length=64)),
        sa.Column("vin", sa.String(length=32)),
        sa.Column("year", sa.Integer),
        sa.Column("model", sa.String(length=32), nullable=False),
        sa.Column("trim", sa.String(length=32)),
        sa.Column("exterior", sa.String(length=64)),
        sa.Column("interior", sa.String(length=64)),
        sa.Column("is_loaner", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("listing_keywords", sa.JSON),
        sa.Column("miles", sa.Integer),
        sa.Column("msrp", sa.Float),
        sa.Column("advertised_price", sa.Float),
        sa.Column("stated_discount", sa.Float),
        sa.Column("dealer_fees", sa.Float),
        sa.Column("incentives", sa.JSON),
        sa.Column("lease_terms", sa.JSON),
        sa.Column("date_first_seen", sa.DateTime, nullable=False),
        sa.Column("date_last_seen", sa.DateTime, nullable=False),
        sa.Column("last_scraped_at", sa.DateTime, nullable=False),
        sa.Column("listing_status", sa.String(length=16), nullable=False, server_default="active"),
        sa.Column("confidence_score", sa.Float, nullable=False, server_default="0"),
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_email", sa.String(length=128), nullable=False),
        sa.Column("min_discount_percent", sa.Float),
        sa.Column("max_miles", sa.Integer),
        sa.Column("max_price", sa.Float),
        sa.Column("states", sa.JSON),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_table(
        "scrape_jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("started_at", sa.DateTime),
        sa.Column("finished_at", sa.DateTime),
        sa.Column("failures", sa.Integer, nullable=False, server_default="0"),
        sa.Column("blocked_domains", sa.JSON),
    )


def downgrade() -> None:
    op.drop_table("scrape_jobs")
    op.drop_table("alerts")
    op.drop_table("listings")
