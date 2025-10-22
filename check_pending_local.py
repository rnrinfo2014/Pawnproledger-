#!/usr/bin/env python3
import sys
sys.path.append('src')
from src.core.pledge_payment_api import get_customer_pending_pledges
from src.core.database import get_db

class FakeUser:
    def __init__(self, id, company_id):
        self.id = id
        self.company_id = company_id


def run_check(customer_id, user_id=6, company_id=1):
    db = next(get_db())
    try:
        user = FakeUser(user_id, company_id)
        resp = get_customer_pending_pledges(customer_id, db, user)
        # resp is a Pydantic model; print dict
        print(resp.dict() if hasattr(resp, 'dict') else resp)
    finally:
        db.close()

if __name__ == '__main__':
    # adjust customer_id if needed
    run_check(1)
