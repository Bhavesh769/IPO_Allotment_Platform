from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.database import get_db
from app.db.models.applications import Application
from app.db.models.ipo import IPO
from app.db.models.users import User
from app.schemas.applications import ApplicationCreate, ApplicationResponse


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

    # Check if IPO exists
    ipo = db.query(IPO).filter(
        IPO.id == application_data.ipo_id
    ).first()

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

    # Check for an existing request
    existing_application = db.query(Application).filter(
        Application.idempotency_key
        == application_data.idempotency_key
    ).first()

    if existing_application:
        return existing_application

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

    try:
        db.add(application)
        db.commit()
        db.refresh(application)

        return application

    except IntegrityError:
        db.rollback()

        existing_application = db.query(Application).filter(
            Application.idempotency_key == application_data.idempotency_key
        ).first()

        if existing_application:
            return existing_application

        raise