from decimal import Decimal

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    user_id: int
    ipo_id: int
    lots_requested: int = Field(gt=0)
    idempotency_key: str


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    ipo_id: int
    lots_requested: int
    amount: Decimal
    status: str

    model_config = {
        "from_attributes": True
    }