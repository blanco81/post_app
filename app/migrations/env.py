import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Caminho para o diretório do projeto
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Importação de configurações e metadados do projeto
from app.core.config import settings
from app.core.deps import metadata
from app.models import post, user  # Modelos necessários para autogeração

# Configuração do Alembic
config = context.config

# Configuração de logging do Alembic
fileConfig(config.config_file_name)

# async_fallback=true is used, because alembic works with sync drivers
SYNC_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"
config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)

#config.set_main_option('sqlalchemy.url', str(settings.DB_DSN)+"?async_fallback=true")
target_metadata = metadata

def run_migrations_offline():
   
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()