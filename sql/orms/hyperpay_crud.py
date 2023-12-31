from sqlalchemy.orm import Session
from sql import models, schemas


def get_payment(db: Session, payment_checkout_id: str):
    db_payment = db.query(models.Payment).filter(
        models.Payment.response.op("->>")("id") == payment_checkout_id and
        models.Payment.integrator == "HyperPay"
    ).first()
    return db_payment.request.get("data").get("entityId") if db_payment else None


def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payment(integrator=payment.integrator, request=payment.request, response=payment.response,
                                status=payment.status, amount=payment.amount, user_id=payment.user_id)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def update_payment(db: Session, payment_checkout_id: str, payment: schemas.PaymentSuccessUpdate):
    db_payment = db.query(models.Payment).filter(
        models.Payment.response.op("->>")("id") == payment_checkout_id and
        models.Payment.integrator == "HyperPay"
    ).update({"integrator": payment.integrator, "response": payment.response, "status": payment.status})
    db.commit()
    return db_payment


def hyperpay_config(db: Session, user_id: int):
    return db.query(models.IntegratorConfig).filter(
        models.IntegratorConfig.providers == "HyperPay" and models.IntegratorConfig.user_id == user_id
    ).first()
