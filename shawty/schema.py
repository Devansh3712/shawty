from datetime import datetime

from pydantic import BaseModel


class Shawty(BaseModel):
    url: str
    hash: str
    timestamp: datetime
    visits: int
