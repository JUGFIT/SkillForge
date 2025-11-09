import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# --------------------------------------------------------------------
# ✅ PATH HANDLING
# --------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(BASE_DIR, "app")

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# --------------------------------------------------------------------
# Import app Base + models
# --------------------------------------------------------------------
from app.core.database import Base
from app import models
from app.core.config import settings

# --------------------------------------------------------------------
# Alembic Config Setup - BULLETPROOF INTERPOLATION FIX
# --------------------------------------------------------------------
config = context.config

# 🛡 CRITICAL FIX: Override the internal file_config to disable interpolation
# This must happen BEFORE any set_main_option calls
if hasattr(config, 'file_config'):
    # Save the old parser
    old_parser = config.file_config
    
    # Import ConfigParser with no interpolation
    from configparser import ConfigParser
    new_parser = ConfigParser(interpolation=None)
    
    # Copy all sections from the old parser
    for section in old_parser.sections():
        if not new_parser.has_section(section):
            new_parser.add_section(section)
        for option in old_parser.options(section):
            value = old_parser.get(section, option, raw=True)
            new_parser.set(section, option, value)
    
    # Replace the file_config completely
    config.file_config = new_parser

# Now it's safe to set the database URL with special characters
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()