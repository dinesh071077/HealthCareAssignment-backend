from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models
from app.schemas import doctor as doctor_schema
from app.db.database import get_db

router = APIRouter(
    prefix="/doctors",
    tags=["doctors"],
)

@router.get("/", response_model=List[doctor_schema.Doctor])
def read_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    doctors = db.query(models.Doctor).offset(skip).limit(limit).all()
    return doctors

@router.post("/", response_model=doctor_schema.Doctor)
def create_doctor(doctor: doctor_schema.DoctorCreate, db: Session = Depends(get_db)):
    db_doctor = models.Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor
