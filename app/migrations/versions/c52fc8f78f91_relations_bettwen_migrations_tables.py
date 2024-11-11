"""Relations bettwen migrations tables

Revision ID: c52fc8f78f91
Revises: eeceb6110212
Create Date: 2024-11-11 04:32:07.273698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c52fc8f78f91'
down_revision = 'eeceb6110212'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('user_id', sa.String(length=30), sa.ForeignKey('users.id')))
    
    op.create_table(
        'post_tags',
        sa.Column('post_id', sa.String(length=30), sa.ForeignKey('posts.id'), primary_key=True),
        sa.Column('tag_id', sa.String(length=30), sa.ForeignKey('tags.id'), primary_key=True)
    )

def downgrade():
    op.drop_table('post_tags')
    op.drop_column('posts', 'user_id')
