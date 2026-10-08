import time

from app.db.database import SessionLocal
from app.services.fund_block_service import expire_fund_blocks


def run_expiry_worker():
    print("Fund block expiry worker started")

    while True:
        db = SessionLocal()

        try:
            expired_count = expire_fund_blocks(db)

            if expired_count > 0:
                print(
                    f"Expired fund blocks: {expired_count}"
                )

        except Exception as exc:
            db.rollback()
            print(f"Expiry worker error: {exc}")

        finally:
            db.close()

        time.sleep(10)


if __name__ == "__main__":
    run_expiry_worker()