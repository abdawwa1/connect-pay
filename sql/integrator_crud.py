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


def update_integrator(db: Session, pk, integrator: serializers.IntegratorCreate):
    db_integrator = db.query(models.IntegratorConfig).filter(models.IntegratorConfig.id == pk).update(
        {
            'providers': integrator.providers,
            'enabled': integrator.enabled,
            'config_data': integrator.config_data
        }
    )
    db.commit()
    return db_integrator


def delete_integrator(db: Session, pk, user_id):
    db.query(models.IntegratorConfig).filter(
        models.IntegratorConfig.id == pk and models.IntegratorConfig.user_id == user_id
    ).delete()

    db.commit()
    return True


def get_integrator(db: Session, provider, user_id):
    return db.query(models.IntegratorConfig).filter(
        models.IntegratorConfig.providers == provider and models.IntegratorConfig.user_id == user_id).first()


def get_integrators(db: Session, user_id):
    return db.query(models.IntegratorConfig).filter(
        models.IntegratorConfig.user_id == user_id
    ).all()


def get_integrator_by_id(db: Session, pk, user_id):
    return db.query(models.IntegratorConfig).filter(
        models.IntegratorConfig.id == pk and models.IntegratorConfig.user_id == user_id).first()
