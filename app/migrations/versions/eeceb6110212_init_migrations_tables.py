"""Init migrations tables

Revision ID: eeceb6110212
Revises: 
Create Date: 2024-11-11 04:22:30.658421

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eeceb6110212'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():    

    # Crear la tabla de usuarios
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=30), primary_key=True),
        sa.Column('name_complete', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=200), unique=True, index=True),
        sa.Column('password', sa.String(length=200), nullable=False),
        sa.Column('role', sa.Enum('admin', 'editor', 'lector', name='userrole'), nullable=False),
        sa.Column('active', sa.Boolean, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Crear la tabla de posts
    op.create_table(
        'posts',
        sa.Column('id', sa.String(length=30), primary_key=True),
        sa.Column('title', sa.String(length=200), unique=True, index=True),
        sa.Column('content', sa.Text),
        sa.Column('deleted', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Crear la tabla de tags
    op.create_table(
        'tags',
        sa.Column('id', sa.String(length=30), primary_key=True),
        sa.Column('name', sa.String(length=200), unique=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )


def downgrade():
    op.drop_table('tags')
    op.drop_table('posts')
    op.drop_table('users')
