"""
Test script to verify payment accounting transactions
This script tests if financial transactions are created during pledge payments
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import (
    Pledge as PledgeModel, 
    Customer as CustomerModel, 
    PledgePayment as PledgePaymentModel,
    LedgerEntry as LedgerEntryModel,
    VoucherMaster as VoucherMasterModel,
    MasterAccount as MasterAccountModel
)
from sqlalchemy import func
from datetime import date, datetime
import requests
import json

def test_payment_accounting():
    """Test if payment creates proper accounting entries"""
    
    print("🧪 Testing Payment Accounting Transactions")
    print("=" * 50)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Find an active pledge for testing
        active_pledge = db.query(PledgeModel).filter(
            PledgeModel.status.in_(['active', 'partial_paid'])
        ).first()
        
        if not active_pledge:
            print("❌ No active pledges found for testing")
            return
        
        print(f"📋 Testing with Pledge: {active_pledge.pledge_no}")
        
        # Get customer info
        customer = db.query(CustomerModel).filter(
            CustomerModel.id == active_pledge.customer_id
        ).first()
        
        print(f"👤 Customer: {customer.name}")
        print(f"🏦 Customer COA Account ID: {customer.coa_account_id}")
        
        # Check current payment balance
        total_payments = db.query(func.sum(PledgePaymentModel.amount)).filter(
            PledgePaymentModel.pledge_id == active_pledge.pledge_id
        ).scalar() or 0.0
        
        remaining_balance = float(active_pledge.final_amount) - total_payments
        print(f"💰 Pledge Amount: {active_pledge.final_amount}")
        print(f"💳 Previous Payments: {total_payments}")
        print(f"📊 Remaining Balance: {remaining_balance}")
        
        # Count ledger entries before payment
        ledger_before = db.query(LedgerEntryModel).filter(
            LedgerEntryModel.reference_type == "payment",
            LedgerEntryModel.reference_id.in_(
                db.query(PledgePaymentModel.payment_id).filter(
                    PledgePaymentModel.pledge_id == active_pledge.pledge_id
                )
            )
        ).count()
        
        vouchers_before = db.query(VoucherMasterModel).filter(
            VoucherMasterModel.voucher_type == "payment"
        ).count()
        
        print(f"📈 Ledger entries before: {ledger_before}")
        print(f"🎫 Vouchers before: {vouchers_before}")
        
        # Make a test payment via API
        test_payment_amount = min(100.0, remaining_balance)
        
        payment_data = {
            "pledge_id": active_pledge.pledge_id,
            "payment_date": date.today().isoformat(),
            "payment_type": "interest",
            "amount": test_payment_amount,
            "interest_amount": 50.0,
            "principal_amount": test_payment_amount - 50.0,
            "penalty_amount": 0.0,
            "discount_amount": 0.0,
            "payment_method": "cash",
            "remarks": "Test payment for accounting verification"
        }
        
        print(f"\n💸 Making test payment of ${test_payment_amount}")
        
        # Make API call (assuming server is running on localhost:8000)
        try:
            response = requests.post(
                "http://localhost:8000/pledge-payments/",
                json=payment_data,
                headers={"Authorization": "Bearer test_token"}  # You might need to get a real token
            )
            
            if response.status_code == 401:
                print("🔐 Authentication required - testing accounting function directly")
                
                # Test accounting function directly
                from pledge_accounting_manager import create_payment_accounting
                
                # Calculate balance after payment
                new_balance = remaining_balance - test_payment_amount
                
                # Create a payment record manually for testing
                test_payment = PledgePaymentModel(
                    pledge_id=active_pledge.pledge_id,
                    payment_date=date.today(),
                    payment_type="interest",
                    amount=test_payment_amount,
                    interest_amount=50.0,
                    principal_amount=test_payment_amount - 50.0,
                    penalty_amount=0.0,
                    discount_amount=0.0,
                    balance_amount=new_balance,  # Add required balance field
                    payment_method="cash",
                    remarks="Test payment for accounting verification",
                    created_by=1,
                    company_id=1,
                    receipt_no="TEST-001"
                )
                
                db.add(test_payment)
                db.flush()
                
                # Test accounting creation
                accounting_result = create_payment_accounting(
                    db=db,
                    payment=test_payment,
                    pledge=active_pledge,
                    customer=customer,
                    company_id=1
                )
                
                print(f"✅ Accounting Result: {json.dumps(accounting_result, indent=2)}")
                
                # Count entries after
                ledger_after = db.query(LedgerEntryModel).filter(
                    LedgerEntryModel.reference_type == "payment",
                    LedgerEntryModel.reference_id == test_payment.payment_id
                ).count()
                
                vouchers_after = db.query(VoucherMasterModel).filter(
                    VoucherMasterModel.voucher_id == accounting_result['voucher_id']
                ).count()
                
                print(f"\n📊 Results:")
                print(f"📈 New ledger entries: {ledger_after}")
                print(f"🎫 New vouchers: {vouchers_after}")
                
                # Show the actual entries
                new_entries = db.query(LedgerEntryModel).filter(
                    LedgerEntryModel.reference_type == "payment",
                    LedgerEntryModel.reference_id == test_payment.payment_id
                ).all()
                
                print(f"\n📋 Accounting Entries Created:")
                for entry in new_entries:
                    account = db.query(MasterAccountModel).filter(
                        MasterAccountModel.id == entry.account_id
                    ).first()
                    print(f"  - {account.account_code if account else 'Unknown'}: Dr. {entry.debit} Cr. {entry.credit} - {entry.description}")
                
                # Rollback test data
                db.rollback()
                print(f"\n🔄 Test data rolled back")
                
            else:
                print(f"API Response: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Payment created successfully via API")
                else:
                    print(f"❌ API Error: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server. Please start the server first.")
            return
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_payment_accounting()