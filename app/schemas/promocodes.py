from datetime import date
from pydantic import BaseModel, Field

class PromocodeCreate(BaseModel):
    code: str
    discount_percent: int = Field(ge = 1, le = 100)
    valid_from: date
    valid_until: date
    max_uses: int


