from datetime import datetime, timezone

from peewee import Model, TextField
from playhouse.sqlite_ext import SqliteExtDatabase

database = SqliteExtDatabase(
    None,
    pragmas={
        'journal_mode': 'wal',
        'cache_size': 50000,
        'foreign_keys': 0,
    },
    autoconnect=False,
    regexp_function=True,
)


def make_pocket_id(x: int | str) -> str:
    return str(x).rjust(15, "-")


def make_pocket_time(dt=None) -> str:
    dt = dt or datetime.now(timezone.utc)
    return dt.isoformat(sep=' ', timespec='milliseconds').replace('+00:00', 'Z')


class BaseModel(Model):
    id = TextField(primary_key=True)
    created = TextField(default=make_pocket_time)
    updated = TextField(default=make_pocket_time)

    class Meta:
        database = database

    @staticmethod
    def make_id(x: int | str) -> str:
        return make_pocket_id(x)

    @staticmethod
    def make_time(dt=None) -> str:
        return make_pocket_time(dt)
