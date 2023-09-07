from sqlalchemy.orm import Session
from sql import models
from src.providers import serializers


def create_integrator(db: Session, integrator: serializers.IntegratorCreate, user_id: str):
    db_integrator = models.IntegratorConfig(providers=integrator.providers, enabled=integrator.enabled,
                                            config_data=integrator.config_data, user_id=user_id)
    db.add(db_integrator)
    db.commit()
    db.refresh(db_integrator)
    return db_integrator


def get_integrator(db: Session, provider, user_id):
    return db.query(models.IntegratorConfig).filter(
        models.IntegratorConfig.providers == provider and models.IntegratorConfig.user_id == user_id).first()
