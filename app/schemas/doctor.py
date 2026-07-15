from pydantic import BaseModel
from typing import Optional

class DoctorBase(BaseModel):
    name: str
    specialization: str
    hospital: str

class DoctorCreate(DoctorBase):
    pass

class Doctor(DoctorBase):
    id: int

    class Config:
        from_attributes = True
