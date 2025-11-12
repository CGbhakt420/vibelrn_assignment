"""Add check constraint for stars range

Revision ID: ce9f21600cfd
Revises: bd0ecbb29785
Create Date: 2025-11-11 09:24:18.851048

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce9f21600cfd'
down_revision: Union[str, None] = 'bd0ecbb29785'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the constraint only if it doesn’t already exist
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT conname FROM pg_constraint
            WHERE conname = 'check_stars_range';
        """)
    )
    exists = result.first() is not None

    if not exists:
        op.create_check_constraint(
            "check_stars_range",
            "review_history",
            "stars >= 1 AND stars <= 10"
        )
    else:
        print("Constraint check_stars_range already exists — skipping creation.")

def downgrade() -> None:
    op.drop_constraint("check_stars_range", "review_history", type_="check")