"""
Payments router.
Handles payment creation, confirmation, and webhook endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentIntentResponse,
    PaymentConfirm,
    WebhookPayload
)
from app.services.payments import PaymentService
from app.routers.users import get_current_user

router = APIRouter()


@router.post("/create", response_model=PaymentIntentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a payment intent for HD image download.
    
    - **job_id**: ID of the image job to unlock HD for
    
    Returns payment details and client secret for frontend payment flow.
    """
    result = await PaymentService.create_payment_intent(
        db=db,
        user_id=current_user.id,
        job_id=payment_data.job_id
    )
    
    return PaymentIntentResponse(
        payment_id=result["payment_id"],
        client_secret=result["client_secret"],
        amount=result["amount"],
        currency=result["currency"]
    )


@router.post("/confirm", response_model=PaymentResponse)
async def confirm_payment(
    confirm_data: PaymentConfirm,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually confirm a payment (for testing or manual verification).
    
    - **payment_id**: ID of the payment to confirm
    - **gateway_reference**: Reference from payment gateway
    """
    payment = await PaymentService.get_payment_by_id(db, confirm_data.payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to confirm this payment"
        )
    
    payment = await PaymentService.confirm_payment(
        db=db,
        payment_id=confirm_data.payment_id,
        gateway_reference=confirm_data.gateway_reference,
        success=True
    )
    
    return payment


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle payment gateway webhook callbacks.
    
    This endpoint is called by the payment gateway (Stripe/Razorpay)
    to notify about payment status changes.
    """
    # In production, verify webhook signature here
    try:
        payload = await request.json()
        webhook_data = WebhookPayload(**payload)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload"
        )
    
    payment = await PaymentService.handle_webhook(
        db=db,
        event_type=webhook_data.event_type,
        gateway_reference=webhook_data.gateway_reference,
        status_str=webhook_data.status
    )
    
    if payment:
        return {"status": "processed", "payment_id": payment.id}
    else:
        return {"status": "ignored"}


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific payment.
    
    - **payment_id**: ID of the payment
    """
    payment = await PaymentService.get_payment_by_id(db, payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )
    
    return payment


@router.get("", response_model=list[PaymentResponse])
async def list_payments(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all payments for the current user.
    
    - **limit**: Maximum number of payments to return
    - **offset**: Number of payments to skip
    """
    payments = await PaymentService.get_user_payments(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return payments
