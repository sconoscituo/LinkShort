from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.payment import Payment
from app.models.user import User


PLANS = {
    "monthly": {"price": 9.99, "days": 30, "currency": "USD"},
    "yearly": {"price": 79.99, "days": 365, "currency": "USD"},
}


async def create_payment(db: AsyncSession, user_id: int, plan: str) -> Payment:
    plan_info = PLANS.get(plan)
    if not plan_info:
        raise ValueError(f"Unknown plan: {plan}")

    payment = Payment(
        user_id=user_id,
        amount=plan_info["price"],
        currency=plan_info["currency"],
        plan=plan,
        status="pending",
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def confirm_payment(db: AsyncSession, payment_id: int, transaction_id: str) -> Payment:
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise ValueError("Payment not found")

    plan_info = PLANS.get(payment.plan)
    payment.status = "completed"
    payment.transaction_id = transaction_id
    payment.is_active = True
    payment.expires_at = datetime.utcnow() + timedelta(days=plan_info["days"])

    user_result = await db.execute(select(User).where(User.id == payment.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.is_premium = True
        user.premium_expires_at = payment.expires_at

    await db.commit()
    await db.refresh(payment)
    return payment
