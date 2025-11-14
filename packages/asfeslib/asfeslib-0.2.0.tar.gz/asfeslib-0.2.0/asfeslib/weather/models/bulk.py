from __future__ import annotations

from typing import List, Optional, Any
from .base import WABaseModel


class BulkLocationRequest(WABaseModel):
    """Описание одной локации в Bulk-запросе."""
    q: str
    custom_id: Optional[str] = None


class BulkQuery(WABaseModel):
    """Тело POST-запроса для Bulk API."""
    locations: List[BulkLocationRequest]


class BulkItem(WABaseModel):
    """Один элемент в ответе Bulk API."""
    query: Any


class BulkResponse(WABaseModel):
    """Ответ Bulk API."""
    bulk: List[BulkItem]
