from app.db.database import SessionLocal
from app.services.fund_block_service import expire_fund_blocks


db = SessionLocal()

try:
    expired_count = expire_fund_blocks(db)
    print(f"Expired fund blocks: {expired_count}")
finally:
    db.close()