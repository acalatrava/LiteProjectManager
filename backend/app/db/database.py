from peewee import SqliteDatabase
from app.core.config import SQLITE_PATH
from contextlib import contextmanager


def get_sqlite_db():
    db = SqliteDatabase(
        SQLITE_PATH,
        pragmas={
            'journal_mode': 'wal',     # Enable WAL mode
            'cache_size': -1024 * 64,  # 64MB page cache
            'foreign_keys': 1,         # Enforce foreign-key constraints
            'synchronous': 0,          # Let OS handle fsync (0=OFF, 1=NORMAL, 2=FULL)
            'journal_size_limit': 1024 * 1024 * 1,  # Limit WAL file to 1MB
        }
    )
    return db


DB = get_sqlite_db()


@contextmanager
def get_db():
    try:
        DB.connect(reuse_if_open=True)
        yield DB
    finally:
        if not DB.is_closed():
            DB.close()
