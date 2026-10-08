from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.fund_blocks import FundBlock


def expire_fund_blocks(db: Session) -> int:
    """
    Mark expired BLOCKED fund blocks as EXPIRED.

    Returns the number of fund blocks expired.
    """

    now = datetime.now(timezone.utc)

    expired_blocks = db.execute(
        select(FundBlock)
        .where(
            FundBlock.status == "BLOCKED",
            FundBlock.expires_at <= now
        )
        .with_for_update()
    ).scalars().all()

    for fund_block in expired_blocks:
        fund_block.status = "EXPIRED"

    db.commit()

    return len(expired_blocks)