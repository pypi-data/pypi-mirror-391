from __future__ import annotations

from typing import List
from .base import WABaseModel
from pydantic import Field


class AlertItem(WABaseModel):
    """Отдельное погодное предупреждение (шторм, наводнение и т.д.)."""
    headline: str
    msgtype: str
    severity: str
    urgency: str
    areas: str
    category: str
    certainty: str
    event: str
    note: str
    effective: str
    expires: str
    desc: str
    instruction: str


class Alerts(WABaseModel):
    """Контейнер для списка предупреждений."""
    alert: List[AlertItem] = Field(default_factory=list)
