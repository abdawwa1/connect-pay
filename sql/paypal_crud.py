from sqlalchemy.orm import Session

from . import models, schemas


def get_payment(db: Session, payment_checkout_id: str):
    db_payment = db.query(models.Payment).filter(
        models.Payment.response.op("->>")("id") == payment_checkout_id and
        models.Payment.integrator == "PayPal"
    ).first()
    return db_payment


def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payment(integrator=payment.integrator, request=payment.request, response=payment.response,
                                status=payment.status, amount=payment.amount)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def update_payment(db: Session, payment_checkout_id: str, payment: schemas.PaymentSuccessUpdate):
    db_payment = db.query(models.Payment).filter(
        models.Payment.response.op("->>")("id") == payment_checkout_id and
        models.Payment.integrator == "PayPal"
    ).update({"integrator": payment.integrator, "response": payment.response, "status": payment.status})
    db.commit()
    return db_payment