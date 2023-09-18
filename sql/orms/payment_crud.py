from sqlalchemy.orm import Session
from sql import models


def get_user_payments(db: Session, user_id):
    return db.query(models.Payment).filter(models.Payment.user_id == user_id).all()
