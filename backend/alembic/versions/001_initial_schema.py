"""Initial database schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asin', sa.String(length=20), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('brand', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=255), nullable=True),
        sa.Column('current_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('list_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('unit_type', sa.String(length=50), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('discount_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('amazon_url', sa.Text(), nullable=False),
        sa.Column('is_prime', sa.Boolean(), server_default='false'),
        sa.Column('is_sponsored', sa.Boolean(), server_default='false'),
        sa.Column('subscribe_save_pct', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('in_stock', sa.Boolean(), server_default='true'),
        sa.Column('savings_vs_category', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('is_best_value', sa.Boolean(), server_default='false'),
        sa.Column('hidden_gem_score', sa.Integer(), nullable=True),
        sa.Column('deal_quality_score', sa.Integer(), nullable=True),
        sa.Column('last_scraped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asin')
    )
    op.create_index('ix_products_asin', 'products', ['asin'], unique=True)
    op.create_index('ix_products_category', 'products', ['category'])
    op.create_index('ix_products_brand', 'products', ['brand'])
    op.create_index('ix_products_unit_price', 'products', ['unit_price'])
    op.create_index('ix_products_rating', 'products', ['rating'])
    op.create_index('ix_products_is_best_value', 'products', ['is_best_value'])
    op.create_index('ix_products_hidden_gem_score', 'products', ['hidden_gem_score'])

    # Create price_history table
    op.create_table(
        'price_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('is_prime', sa.Boolean(), nullable=True),
        sa.Column('is_sponsored', sa.Boolean(), nullable=True),
        sa.Column('in_stock', sa.Boolean(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_price_history_product_id', 'price_history', ['product_id'])
    op.create_index('ix_price_history_recorded_at', 'price_history', ['recorded_at'])

    # Create search_queries table
    op.create_table(
        'search_queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.String(length=500), nullable=False),
        sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('results_count', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_search_queries_query_text', 'search_queries', ['query_text'])
    op.create_index('ix_search_queries_created_at', 'search_queries', ['created_at'])
    op.create_index('ix_search_queries_user_id', 'search_queries', ['user_id'])

    # Create price_alerts table
    op.create_table(
        'price_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('target_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_price_alerts_user_id', 'price_alerts', ['user_id'])
    op.create_index('ix_price_alerts_product_id', 'price_alerts', ['product_id'])
    op.create_index('ix_price_alerts_is_active', 'price_alerts', ['is_active'])


def downgrade() -> None:
    # Drop tables in reverse order (to avoid FK constraint issues)
    op.drop_table('price_alerts')
    op.drop_table('search_queries')
    op.drop_table('price_history')
    op.drop_table('products')
    op.drop_table('users')
