#!/usr/bin/env python3
import sys
from datetime import datetime
# ensure package imports work
sys.path.append('src')

from core.database import get_db
from core.models import PledgePayment, LedgerEntry, Pledge, VoucherMaster, MasterAccount, Customer
from sqlalchemy import func


def show_recent_payments(limit=10):
    db = next(get_db())
    try:
        payments = db.query(PledgePayment).order_by(PledgePayment.created_at.desc()).limit(limit).all()
        print(f"Found {len(payments)} recent payments:\n")
        for p in payments:
            print(f"Payment id(db): {p.payment_id}, pledge_id: {p.pledge_id}, amount: {p.amount}, interest: {p.interest_amount}, principal: {p.principal_amount}, penalty: {p.penalty_amount}, date: {p.payment_date}, created_by: {p.created_by}")
            # ledger entries linked to this payment
            entries = db.query(LedgerEntry).filter(LedgerEntry.reference_type=='payment', LedgerEntry.reference_id==p.payment_id).all()
            print(f"  Linked ledger entries ({len(entries)}):")
            for e in entries:
                acct = db.query(MasterAccount).filter(MasterAccount.account_id==e.account_id).first()
                acct_code = acct.account_code if acct else e.account_id
                print(f"    Entry id: {e.entry_id}, acct: {acct_code}, dr: {e.debit}, cr: {e.credit}, amount: {e.amount}, narr: {e.narration}")
            # compute pledge remaining by ledger or payments
            pledge = db.query(Pledge).filter(Pledge.pledge_id==p.pledge_id).first()
            if pledge:
                # sum payments for this pledge using SQLAlchemy func.sum
                total_paid = db.query(func.sum(PledgePayment.amount)).filter(PledgePayment.pledge_id==pledge.pledge_id).scalar() or 0
                print(f"  Pledge {pledge.pledge_no} total loan: {pledge.total_loan_amount}, total_paid: {total_paid}, remaining(principal field): {pledge.remaining_principal if hasattr(pledge, 'remaining_principal') else 'N/A'}")
            print("")
    finally:
        db.close()

if __name__ == '__main__':
    show_recent_payments(10)
