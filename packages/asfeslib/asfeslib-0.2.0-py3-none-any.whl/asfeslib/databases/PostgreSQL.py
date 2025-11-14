from typing import Optional, Tuple
import psycopg
from psycopg import AsyncConnection
from pydantic import BaseModel, Field
from asfeslib.core.logger import Logger

logger = Logger(name=__name__)


class PostgresConnectScheme(BaseModel):
    db_url: Optional[str] = Field(
        default=None,
        description="Полная ссылка подключения (например, postgresql://user:pass@host:port/db)"
    )
    host: str = Field(default="localhost", description="Хост PostgreSQL")
    port: int = Field(default=5432, description="Порт PostgreSQL")
    username: str = Field(default="postgres", description="Имя пользователя")
    password: Optional[str] = Field(default=None, description="Пароль")
    db_name: str = Field(default="hackathon_db", description="Имя базы данных")

    def assemble_url(self) -> str:
        if self.db_url:
            return self.db_url
        auth = f"{self.username}:{self.password}@" if self.password else f"{self.username}@"
        return f"postgresql://{auth}{self.host}:{self.port}/{self.db_name}"


async def connect_postgres(data: PostgresConnectScheme) -> Tuple[AsyncConnection, bool]:
    """
    Создаёт асинхронное подключение к PostgreSQL через psycopg3.
    Возвращает (connection, status)
    """
    conn: Optional[AsyncConnection] = None
    status = False

    try:
        conn = await psycopg.AsyncConnection.connect(data.assemble_url())
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1;")
            row = await cur.fetchone()
            status = row and row[0] == 1

        if status:
            logger.info(f"Подключение к PostgreSQL установлено: {data.host}:{data.port}/{data.db_name}")
        else:
            logger.error("PostgreSQL не ответил корректно на SELECT 1")

    except Exception as e:
        logger.error(f"Ошибка подключения к PostgreSQL: {e}")

    return conn, status
