from typing import Optional, Tuple
import aiomysql
from pydantic import BaseModel, Field
from asfeslib.core.logger import Logger

logger = Logger(name=__name__)


class MariaConnectScheme(BaseModel):
    db_url: Optional[str] = Field(
        default=None,
        description="Полная ссылка подключения (например, mysql://user:pass@host:port/db)"
    )
    host: str = Field(default="localhost", description="Хост базы данных")
    port: int = Field(default=3306, description="Порт MariaDB/MySQL")
    username: str = Field(default="root", description="Имя пользователя")
    password: Optional[str] = Field(default=None, description="Пароль пользователя")
    db_name: str = Field(default="hackathon_db", description="Имя базы данных")

    def assemble_url(self) -> str:
        if self.db_url:
            return self.db_url
        auth = f"{self.username}:{self.password}@" if self.password else f"{self.username}@"
        return f"mysql://{auth}{self.host}:{self.port}/{self.db_name}"


async def connect_mariadb(data: MariaConnectScheme) -> Tuple[aiomysql.Connection, bool]:
    """
    Создаёт асинхронное подключение к MariaDB через aiomysql.
    Возвращает (connection, status)
    """
    conn = None
    status = False

    try:
        conn = await aiomysql.connect(
            host=data.host,
            port=data.port,
            user=data.username,
            password=data.password,
            db=data.db_name,
            autocommit=True,
        )

        async with conn.cursor() as cur:
            await cur.execute("SELECT 1;")
            result = await cur.fetchone()
            status = bool(result and result[0] == 1)

        if status:
            logger.info(f"Подключение к MariaDB установлено: {data.host}:{data.port}/{data.db_name}")
        else:
            logger.error("MariaDB не ответила корректно на SELECT 1")

    except Exception as e:
        logger.error(f"Ошибка подключения к MariaDB: {e}")

    return conn, status
