"""
Seed the database with sample doctors and interactions.
Run: python seed.py  (from the backend directory, with venv active)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db.database import SessionLocal, engine
from app.db import models
from app.db.database import Base
from datetime import date

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Doctors ────────────────────────────────────────────────────────────────
doctors_data = [
    {"name": "Dr. Rajesh Sharma",  "specialization": "Cardiologist",        "hospital": "Apollo Hospital Chennai"},
    {"name": "Dr. Priya Patel",    "specialization": "Neurologist",          "hospital": "Fortis Hospital Bangalore"},
    {"name": "Dr. Anil Rao",       "specialization": "General Physician",    "hospital": "Columbia Asia Hyderabad"},
    {"name": "Dr. Meera Nair",     "specialization": "Endocrinologist",      "hospital": "Manipal Hospital Kochi"},
    {"name": "Dr. Suresh Kumar",   "specialization": "Pulmonologist",        "hospital": "Max Hospital Delhi"},
]

doctors = []
for d in doctors_data:
    existing = db.query(models.Doctor).filter(models.Doctor.name == d["name"]).first()
    if not existing:
        doc = models.Doctor(**d)
        db.add(doc)
        db.flush()
        doctors.append(doc)
    else:
        doctors.append(existing)

db.commit()
print(f"Seeded {len(doctors)} doctors")

# ── Interactions ───────────────────────────────────────────────────────────
interactions_data = [
    {
        "doctor_id": doctors[0].id,
        "visit_date": date(2026, 7, 10),
        "visit_type": "In-person",
        "purpose": "CardioPlus product launch",
        "summary": "Discussed benefits of CardioPlus for atrial fibrillation management. Doctor showed strong interest and requested samples.",
        "sentiment": "Positive",
        "products": ["CardioPlus", "NeuroMax"],
        "follow_up_date": date(2026, 7, 24),
        "outcome": "Sample Requested",
    },
    {
        "doctor_id": doctors[1].id,
        "visit_date": date(2026, 7, 11),
        "visit_type": "Phone",
        "purpose": "NeuroMax follow-up",
        "summary": "Doctor asked for clinical trial data on NeuroMax. Neutral response, wants to review literature first.",
        "sentiment": "Neutral",
        "products": ["NeuroMax"],
        "follow_up_date": date(2026, 7, 28),
        "outcome": "Follow-up Needed",
    },
    {
        "doctor_id": doctors[2].id,
        "visit_date": date(2026, 7, 12),
        "visit_type": "In-person",
        "purpose": "DiabetiCare introduction",
        "summary": "Doctor currently using competitor product. Not interested in switching. Price is a concern.",
        "sentiment": "Negative",
        "products": ["DiabetiCare"],
        "outcome": "No Action",
    },
    {
        "doctor_id": doctors[3].id,
        "visit_date": date(2026, 7, 13),
        "visit_type": "Video",
        "purpose": "OncoPrime awareness",
        "summary": "Detailed demo of OncoPrime. Doctor is interested and will discuss with department head.",
        "sentiment": "Positive",
        "products": ["OncoPrime", "ImmunBoost"],
        "follow_up_date": date(2026, 7, 27),
        "outcome": "Prescription Interest",
    },
]

for i_data in interactions_data:
    interaction = models.Interaction(**i_data)
    db.add(interaction)

db.commit()
print(f"Seeded {len(interactions_data)} interactions")
print("\nDatabase seeded successfully!")
db.close()
