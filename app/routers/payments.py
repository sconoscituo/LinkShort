from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.payment import create_payment, confirm_payment, PLANS

router = APIRouter(prefix="/api/payments", tags=["payments"])


class PaymentCreate(BaseModel):
    plan: str


class PaymentConfirm(BaseModel):
    payment_id: int
    transaction_id: str


@router.get("/plans")
async def get_plans():
    return {"plans": PLANS}


@router.post("/create")
async def initiate_payment(
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    payment = await create_payment(db, current_user.id, payload.plan)
    return {"payment_id": payment.id, "amount": payment.amount, "currency": payment.currency, "status": payment.status}


@router.post("/confirm")
async def confirm(
    payload: PaymentConfirm,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        payment = await confirm_payment(db, payload.payment_id, payload.transaction_id)
        return {"status": "success", "is_premium": True, "expires_at": str(payment.expires_at)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
