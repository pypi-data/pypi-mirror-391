from asfeslib.databases.MongoDB import connect_mongo
from asfeslib.databases.PostgreSQL import connect_postgres
from asfeslib.databases.MySQL import connect_mariadb

async def connect_database(db_type: str, config):
    """Подключение к нужной БД по типу."""
    if db_type == "mongo":
        return await connect_mongo(config)
    if db_type == "postgres":
        return await connect_postgres(config)
    if db_type in ("mariadb", "mysql"):
        return await connect_mariadb(config)
    raise ValueError(f"Unknown db_type: {db_type}")
