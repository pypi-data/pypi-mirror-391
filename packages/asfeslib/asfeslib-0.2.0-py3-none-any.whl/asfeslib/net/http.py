import aiohttp
import asyncio
from typing import Optional, Any, Dict
from asfeslib.core.logger import Logger

logger = Logger(name=__name__)


class HTTPClient:
    """
    Асинхронный HTTP-клиент на базе aiohttp.
    Поддерживает JSON, текст, бинарные запросы и автоматическое логирование.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 2,
    ):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Закрыть соединение."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Any = None,
        data: Any = None,
        retry: Optional[int] = None,
        raise_on_fail: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Универсальный HTTP-запрос с retry, логированием и JSON-ответом.
        """
        full_url = url if url.startswith("http") else f"{self.base_url}/{url.lstrip('/')}"
        retries = retry if retry is not None else self.max_retries

        for attempt in range(1, retries + 1):
            try:
                async with self.session.request(
                    method=method.upper(),
                    url=full_url,
                    params=params,
                    headers=headers,
                    json=json,
                    data=data,
                ) as response:
                    status = response.status
                    content_type = response.headers.get("Content-Type", "")
                    logger.debug(f"{method.upper()} {full_url} → {status}")

                    if "application/json" in content_type:
                        result = await response.json()
                    elif "text" in content_type:
                        result = await response.text()
                    else:
                        result = await response.read()

                    if 200 <= status < 300:
                        return result

                    logger.warning(f"{method.upper()} {full_url} вернул {status}")
                    if raise_on_fail:
                        response.raise_for_status()
                    return None

            except asyncio.TimeoutError:
                logger.error(f"Таймаут при запросе {method.upper()} {full_url}")
            except aiohttp.ClientError as e:
                logger.error(f"Ошибка HTTP: {e}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка при запросе: {e}")

            if attempt < retries:
                await asyncio.sleep(0.5 * attempt)
                logger.debug(f"🔁 Повтор {attempt}/{retries} для {method.upper()} {full_url}")

        logger.error(f"Не удалось выполнить запрос {method.upper()} {full_url} после {retries} попыток")
        return None

    async def get(self, url: str, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs):
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs):
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs):
        return await self.request("DELETE", url, **kwargs)
