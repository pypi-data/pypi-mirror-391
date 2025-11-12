from alembic.config import Config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from .project import find_project_root, get_settings


def get_alembic_config() -> Config:
    """Load Alembic config from project root and inject DB_URL, script
    location, and log level.

    """
    root = find_project_root()

    ini_path = root / "alembic.ini"
    migrations_dir = root / "migrations"

    if not ini_path.exists():
        raise FileNotFoundError(f"No alembic.ini found in {root}")

    settings = get_settings(force_reload=True)

    cfg = Config(str(ini_path))
    cfg.set_main_option("sqlalchemy.url", settings.DB_URL)
    cfg.set_main_option("script_location", str(migrations_dir))
    cfg.set_main_option("logger_alembic.level", settings.LOG_LEVEL)
    cfg.config_file_name = str(ini_path)

    return cfg


def run_migrations_offline(context, target_metadata):
    # turn url into sync if it is async?
    config = context.config
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


async def async_run_migrations_online(context, target_metadata):
    # turn url into async if it is sync?
    config = context.config
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn,
                target_metadata=target_metadata,
            )
        )

        def do_run_migrations(sync_connection):
            with sync_connection.begin():
                context.run_migrations()

        await connection.run_sync(do_run_migrations)
