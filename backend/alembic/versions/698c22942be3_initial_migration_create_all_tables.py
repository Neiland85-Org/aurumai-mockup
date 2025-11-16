"""Initial migration - create all tables

Revision ID: 698c22942be3
Revises:
Create Date: 2025-11-15 19:02:46.755119

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op  # type: ignore

# revision identifiers, used by Alembic.
revision: str = "698c22942be3"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create machines table
    op.create_table(
        "machines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.String(length=50), nullable=False),
        sa.Column("machine_type", sa.String(length=50), nullable=False),
        sa.Column("location", sa.String(length=100), nullable=False),
        sa.Column("operational", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("machine_id"),
    )
    op.create_index(
        op.f("ix_machines_machine_id"), "machines", ["machine_id"], unique=False
    )

    # Create raw_measurements table (will be converted to TimescaleDB hypertable)
    op.create_table(
        "raw_measurements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.String(length=50), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.machine_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_raw_measurements_machine_id"),
        "raw_measurements",
        ["machine_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_raw_measurements_timestamp"),
        "raw_measurements",
        ["timestamp"],
        unique=False,
    )

    # Create features table
    op.create_table(
        "features",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.String(length=50), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.machine_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_features_machine_id"), "features", ["machine_id"], unique=False
    )
    op.create_index(
        op.f("ix_features_timestamp"), "features", ["timestamp"], unique=False
    )

    # Create predictions table (will be converted to TimescaleDB hypertable)
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.String(length=50), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("failure_probability", sa.Float(), nullable=False),
        sa.Column("maintenance_hours", sa.Integer(), nullable=False),
        sa.Column("failure_type", sa.String(length=100), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("model_version", sa.String(length=50), nullable=True),
        sa.Column("features_used", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.machine_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_predictions_machine_id"), "predictions", ["machine_id"], unique=False
    )
    op.create_index(
        op.f("ix_predictions_timestamp"), "predictions", ["timestamp"], unique=False
    )

    # Create esg_records table (will be converted to TimescaleDB hypertable)
    op.create_table(
        "esg_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.String(length=50), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("instant_co2eq_kg", sa.Float(), nullable=False),
        sa.Column("cumulative_co2eq_kg", sa.Float(), nullable=False),
        sa.Column("fuel_rate_lh", sa.Float(), nullable=True),
        sa.Column("power_consumption_kw", sa.Float(), nullable=True),
        sa.Column("efficiency_score", sa.Float(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.machine_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_esg_records_machine_id"), "esg_records", ["machine_id"], unique=False
    )
    op.create_index(
        op.f("ix_esg_records_timestamp"), "esg_records", ["timestamp"], unique=False
    )

    # Create alerts table
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("machine_id", sa.String(length=50), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("acknowledged", sa.Boolean(), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.Column("acknowledged_by", sa.String(length=100), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["machine_id"],
            ["machines.machine_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_alerts_machine_id"), "alerts", ["machine_id"], unique=False
    )
    op.create_index(op.f("ix_alerts_timestamp"), "alerts", ["timestamp"], unique=False)

    # Enable TimescaleDB extension
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

    # Convert time-series tables to hypertables
    op.execute(
        """
        SELECT create_hypertable(
            'raw_measurements',
            'timestamp',
            if_not_exists => TRUE,
            migrate_data => TRUE
        );
    """
    )

    op.execute(
        """
        SELECT create_hypertable(
            'predictions',
            'timestamp',
            if_not_exists => TRUE,
            migrate_data => TRUE
        );
    """
    )

    op.execute(
        """
        SELECT create_hypertable(
            'esg_records',
            'timestamp',
            if_not_exists => TRUE,
            migrate_data => TRUE
        );
    """
    )


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("alerts")
    op.drop_table("esg_records")
    op.drop_table("predictions")
    op.drop_table("features")
    op.drop_table("raw_measurements")
    op.drop_table("machines")

    # Note: TimescaleDB extension is not dropped to avoid affecting other databases
