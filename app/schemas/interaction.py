from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime

class InteractionBase(BaseModel):
    doctor_id: int
    visit_date: date
    visit_time: Optional[time] = None
    visit_type: str
    purpose: Optional[str] = None
    summary: str
    sentiment: str
    products: List[str]
    follow_up_date: Optional[date] = None
    outcome: Optional[str] = None

class InteractionCreate(InteractionBase):
    pass

class Interaction(InteractionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
