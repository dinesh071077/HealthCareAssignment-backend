from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    specialization = Column(String(255))
    hospital = Column(String(255))

    interactions = relationship("Interaction", back_populates="doctor")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    visit_date = Column(Date)
    visit_time = Column(Time, nullable=True)
    visit_type = Column(String(50))
    purpose = Column(Text, nullable=True)
    summary = Column(Text)
    sentiment = Column(String(50))
    products = Column(JSON)
    follow_up_date = Column(Date, nullable=True)
    outcome = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    doctor = relationship("Doctor", back_populates="interactions")
