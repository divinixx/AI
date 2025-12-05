"""
Payment service.
Handles payment gateway integration (Stripe/Razorpay) for HD image downloads.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from decimal import Decimal
import logging

from app.config import settings
from app.models.payment import Payment, PaymentStatus
from app.models.image_job import ImageJob

logger = logging.getLogger(__name__)

# HD Download price
HD_DOWNLOAD_PRICE = Decimal("2.99")
HD_DOWNLOAD_CURRENCY = "USD"


class PaymentService:
    """Payment service for handling HD image download purchases."""
    
    @staticmethod
    async def create_payment_intent(
        db: AsyncSession,
        user_id: int,
        job_id: int
    ) -> dict:
        """
        Create a payment intent for HD download.
        Returns payment record and gateway-specific client secret.
        """
        # Verify job exists and belongs to user
        result = await db.execute(
            select(ImageJob).where(
                ImageJob.id == job_id,
                ImageJob.user_id == user_id
            )
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image job not found"
            )
        
        if job.is_hd_unlocked == "Y":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="HD already unlocked for this image"
            )
        
        # Check for existing pending payment
        result = await db.execute(
            select(Payment).where(
                Payment.job_id == job_id,
                Payment.status == PaymentStatus.PENDING
            )
        )
        existing_payment = result.scalar_one_or_none()
        
        if existing_payment:
            # Return existing pending payment
            return {
                "payment_id": existing_payment.id,
                "client_secret": f"mock_client_secret_{existing_payment.id}",
                "amount": existing_payment.amount,
                "currency": existing_payment.currency
            }
        
        # Create new payment record
        payment = Payment(
            user_id=user_id,
            job_id=job_id,
            amount=HD_DOWNLOAD_PRICE,
            currency=HD_DOWNLOAD_CURRENCY,
            status=PaymentStatus.PENDING
        )
        db.add(payment)
        await db.flush()
        await db.refresh(payment)
        
        # In a real implementation, create payment intent with Stripe/Razorpay
        # client_secret = stripe.PaymentIntent.create(...)
        client_secret = f"mock_client_secret_{payment.id}"
        
        logger.info(f"Created payment intent {payment.id} for job {job_id}")
        
        return {
            "payment_id": payment.id,
            "client_secret": client_secret,
            "amount": payment.amount,
            "currency": payment.currency
        }
    
    @staticmethod
    async def confirm_payment(
        db: AsyncSession,
        payment_id: int,
        gateway_reference: str,
        success: bool = True
    ) -> Payment:
        """
        Confirm a payment and unlock HD download if successful.
        """
        result = await db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != PaymentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already processed"
            )
        
        # Update payment status
        payment.gateway_reference = gateway_reference
        payment.status = PaymentStatus.SUCCESS if success else PaymentStatus.FAILED
        
        if success:
            # Unlock HD download for the job
            result = await db.execute(
                select(ImageJob).where(ImageJob.id == payment.job_id)
            )
            job = result.scalar_one_or_none()
            if job:
                job.is_hd_unlocked = "Y"
        
        await db.flush()
        await db.refresh(payment)
        
        logger.info(f"Payment {payment_id} confirmed with status: {payment.status}")
        
        return payment
    
    @staticmethod
    async def handle_webhook(
        db: AsyncSession,
        event_type: str,
        gateway_reference: str,
        status_str: str
    ) -> Optional[Payment]:
        """
        Handle payment gateway webhook callback.
        """
        # Find payment by gateway reference
        result = await db.execute(
            select(Payment).where(Payment.gateway_reference == gateway_reference)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            logger.warning(f"Webhook received for unknown payment: {gateway_reference}")
            return None
        
        # Map gateway status to our status
        status_map = {
            "succeeded": PaymentStatus.SUCCESS,
            "payment_intent.succeeded": PaymentStatus.SUCCESS,
            "failed": PaymentStatus.FAILED,
            "payment_intent.payment_failed": PaymentStatus.FAILED,
        }
        
        new_status = status_map.get(status_str) or status_map.get(event_type)
        if new_status:
            payment.status = new_status
            
            if new_status == PaymentStatus.SUCCESS:
                # Unlock HD download
                result = await db.execute(
                    select(ImageJob).where(ImageJob.id == payment.job_id)
                )
                job = result.scalar_one_or_none()
                if job:
                    job.is_hd_unlocked = "Y"
            
            await db.flush()
            await db.refresh(payment)
        
        return payment
    
    @staticmethod
    async def get_payment_by_id(db: AsyncSession, payment_id: int) -> Optional[Payment]:
        """Get a payment by ID."""
        result = await db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_payments(
        db: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[Payment]:
        """Get all payments for a user."""
        result = await db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
