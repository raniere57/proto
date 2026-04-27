"""Stamp initial state: database already created by Django

This migration only marks the current database state as the initial Alembic
revision, since all tables already exist from Django's migrations.
Run: alembic stamp 001

Revision ID: 001
Revises:
Create Date: 2026-04-27
"""
from typing import Sequence, Union
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Database already has all tables from Django migrations.
    # This is a stamp-only revision to let Alembic know the baseline.
    pass


def downgrade() -> None:
    pass
