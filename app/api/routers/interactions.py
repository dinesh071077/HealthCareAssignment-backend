from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import models
from app.schemas import interaction as interaction_schema
from app.db.database import get_db

router = APIRouter(
    prefix="/interactions",
    tags=["interactions"],
)

@router.post("", response_model=interaction_schema.Interaction)
def create_interaction(interaction: interaction_schema.InteractionCreate, db: Session = Depends(get_db)):
    db_interaction = models.Interaction(**interaction.model_dump())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@router.get("", response_model=List[interaction_schema.Interaction])
def read_interactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    interactions = db.query(models.Interaction).offset(skip).limit(limit).all()
    return interactions

@router.get("/{interaction_id}", response_model=interaction_schema.Interaction)
def read_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
    if interaction is None:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction
