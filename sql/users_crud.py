from sqlalchemy.orm import Session
from . import models, schemas


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(user_name=user.user_name, external_id=user.external_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, external_id: str):
    return db.query(models.User).filter(models.User.external_id == external_id).first()
