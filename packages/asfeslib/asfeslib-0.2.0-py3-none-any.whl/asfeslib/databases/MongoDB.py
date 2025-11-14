from typing import Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, AnyUrl, Field
from asfeslib.core.logger import Logger

logger = Logger(name=__name__)


class MongoConnectScheme(BaseModel):
    db_url: Optional[AnyUrl] = Field(
        default=None,
        description="Полная ссылка подключения MongoDB (например, mongodb://user:pass@host:port/db)",
    )

    host: str = Field(default="localhost", description="Хост MongoDB")
    port: int = Field(default=27017, description="Порт MongoDB")
    username: Optional[str] = Field(default=None, description="Имя пользователя")
    password: Optional[str] = Field(default=None, description="Пароль")
    db_name: str = Field(default="hackathon_db", description="Имя базы данных")

    def assemble_url(self) -> str:
        if self.db_url:
            return str(self.db_url)

        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"

        return f"mongodb://{auth}{self.host}:{self.port}/{self.db_name}"


async def connect_mongo(data: MongoConnectScheme) -> Tuple[AsyncIOMotorClient, AsyncIOMotorDatabase, bool]:
    """
    Создаёт асинхронное подключение к MongoDB через Motor.
    Принимает либо готовый db_url, либо отдельные поля.
    Возвращает (клиент, база данных, статус подключения).
    """
    mongo_uri = data.assemble_url()
    client = AsyncIOMotorClient(mongo_uri)
    db = client[data.db_name]
    status = False

    try:
        result = await client.admin.command("ping")
        status = result.get("ok", 0) == 1.0
        if status:
            logger.info(f"Подключение к MongoDB установлено: {mongo_uri}")
        else:
            logger.error(f"MongoDB вернул некорректный ответ на ping: {result}")
    except Exception as e:
        logger.error(f"Ошибка подключения к MongoDB: {e}")

    return client, db, status
