from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.db.database import get_db
from app.db.models.applications import Application
from app.db.models.ipo import IPO
from app.db.models.users import User
from app.schemas.applications import ApplicationCreate, ApplicationResponse
from app.db.models.fund_blocks import FundBlock

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


@router.post("/", response_model=ApplicationResponse)
def create_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    user = db.query(User).filter(
        User.id == application_data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check if this request was already processed
    existing_application = db.query(Application).filter(
        Application.idempotency_key
        == application_data.idempotency_key
    ).first()

    if existing_application:
        return existing_application

    # Lock the IPO row for this transaction
    ipo = db.execute(
        select(IPO)
        .where(IPO.id == application_data.ipo_id)
        .with_for_update()
    ).scalar_one_or_none()

    if not ipo:
        raise HTTPException(
            status_code=404,
            detail="IPO not found"
        )

    # Check if IPO is open
    if ipo.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="IPO is not open for applications"
        )

    # Check whether enough lots are available
    if application_data.lots_requested > ipo.available_lots:
        raise HTTPException(
            status_code=400,
            detail="Not enough lots available"
        )

    # Calculate application amount
    amount = (
        application_data.lots_requested
        * ipo.lot_size
        * ipo.price
    )

    # Create application
    application = Application(
        user_id=application_data.user_id,
        ipo_id=application_data.ipo_id,
        lots_requested=application_data.lots_requested,
        amount=amount,
        status="PENDING",
        idempotency_key=application_data.idempotency_key,
    )

    db.add(application)
    db.flush()

    ipo.available_lots -= application_data.lots_requested

    fund_block = FundBlock(
        application_id=application.id,
        amount=amount,
        status="BLOCKED",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    db.add(fund_block)

    try:
        db.commit()
        db.refresh(application)

        return application

    except IntegrityError:
        db.rollback()
        
        existing_application = db.query(Application).filter(
            Application.idempotency_key
            == application_data.idempotency_key
        ).first()

        if existing_application:
            return existing_application

        raise