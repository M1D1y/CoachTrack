"""Require a unique normalized user name without changing existing rows.

Revision ID: 0002
Revises: 0001
"""
from alembic import context, op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

NORMALIZED_NAME = (
    "translate(lower(btrim(regexp_replace(name, '[[:space:]]+', ' ', 'g'))), "
    "'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')"
)


def upgrade():
    if context.is_offline_mode():
        op.execute(f'''
            DO $$ BEGIN
                IF EXISTS (
                    SELECT 1 FROM users
                    GROUP BY {NORMALIZED_NAME}
                    HAVING count(*) > 1
                ) THEN
                    RAISE EXCEPTION 'Duplicate normalized users.name values; resolve them before migration';
                END IF;
            END $$
        ''')
        op.execute(f'CREATE UNIQUE INDEX uq_users_name_normalized ON users ({NORMALIZED_NAME})')
        return

    connection = op.get_bind()
    # Keep the duplicate check and index creation in the same transaction.
    connection.execute(sa.text('LOCK TABLE users IN SHARE ROW EXCLUSIVE MODE'))
    duplicates = connection.execute(sa.text(f'''
        SELECT {NORMALIZED_NAME} AS name_key, array_agg(id ORDER BY id) AS user_ids
        FROM users
        GROUP BY {NORMALIZED_NAME}
        HAVING count(*) > 1
        LIMIT 10
    ''')).all()
    if duplicates:
        details = '; '.join(f'{row.name_key}: ID {row.user_ids}' for row in duplicates)
        raise RuntimeError(
            'Найдены пользователи с одинаковым ФИО после нормализации: '
            f'{details}. Разберите конфликт вручную; данные не изменены.'
        )
    op.execute(f'CREATE UNIQUE INDEX uq_users_name_normalized ON users ({NORMALIZED_NAME})')


def downgrade():
    op.drop_index('uq_users_name_normalized', table_name='users')
