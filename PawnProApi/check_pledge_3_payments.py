"""
Check all payments for pledge 3 to understand the first interest payment issue
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def check_pledge_3_payments():
    """Check all payments for pledge 3"""
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as db:
            print("🔍 Checking all payments for Pledge 3...")
            print("=" * 60)
            
            # Get pledge details first
            pledge_result = db.execute(text("""
                SELECT 
                    pledge_no,
                    total_loan_amount,
                    first_month_interest,
                    document_charges,
                    final_amount,
                    status,
                    pledge_date
                FROM pledges 
                WHERE pledge_id = 3
            """))
            
            pledge = pledge_result.fetchone()
            if not pledge:
                print("❌ Pledge 3 not found!")
                return
                
            print(f"📋 Pledge {pledge[0]} Details:")
            print(f"   Loan Amount: {pledge[1]:,.2f}")
            print(f"   First Month Interest: {pledge[2]:,.2f}")
            print(f"   Document Charges: {pledge[3]:,.2f}")
            print(f"   Final Amount: {pledge[4]:,.2f}")
            print(f"   Status: {pledge[5]}")
            print(f"   Pledge Date: {pledge[6]}")
            
            # Get all payments
            payment_result = db.execute(text("""
                SELECT 
                    payment_id,
                    amount,
                    payment_type,
                    receipt_no,
                    payment_date,
                    balance_amount,
                    interest_amount,
                    principal_amount,
                    remarks,
                    created_at
                FROM pledge_payments 
                WHERE pledge_id = 3 
                ORDER BY created_at
            """))
            
            payments = payment_result.fetchall()
            
            print(f"\n💰 All Payments ({len(payments)} total):")
            print("-" * 80)
            
            total_paid = 0
            for i, payment in enumerate(payments, 1):
                amount = float(payment[1])
                total_paid += amount
                
                print(f"Payment {i} (ID: {payment[0]}):")
                print(f"   Amount: {amount:,.2f}")
                print(f"   Type: {payment[2]}")
                print(f"   Receipt: {payment[3]}")
                print(f"   Date: {payment[4]}")
                print(f"   Balance After: {payment[5]:,.2f}")
                print(f"   Interest: {payment[6]:,.2f}")
                print(f"   Principal: {payment[7]:,.2f}")
                if payment[8]:
                    print(f"   Remarks: {payment[8]}")
                print(f"   Created: {payment[9]}")
                print()
            
            print(f"📊 Summary:")
            print(f"   Total Payments Made: {total_paid:,.2f}")
            print(f"   Final Amount: {pledge[4]:,.2f}")
            print(f"   Calculated Balance: {pledge[4] - total_paid:,.2f}")
            
            # Check if there should be an automatic first interest payment
            expected_balance = pledge[4] - total_paid
            print(f"\n🔍 Analysis:")
            
            if expected_balance <= 0.01:
                print(f"   ✅ Pledge should be REDEEMED (fully paid)")
            elif total_paid > 0:
                print(f"   🔄 Pledge should be PARTIAL_PAID")
            else:
                print(f"   📋 Pledge should be ACTIVE")
                
            print(f"   Current Status: {pledge[5]}")
            
            # Look for first interest payment pattern
            first_interest_payment = None
            for payment in payments:
                if payment[2] and 'first' in payment[2].lower():
                    first_interest_payment = payment
                    break
                elif payment[3] and payment[3].startswith('FI-'):
                    first_interest_payment = payment
                    break
            
            if first_interest_payment:
                print(f"\n🎯 Found First Interest Payment:")
                print(f"   Receipt: {first_interest_payment[3]}")
                print(f"   Amount: {first_interest_payment[1]:,.2f}")
                print(f"   Type: {first_interest_payment[2]}")
            else:
                print(f"\n❓ No automatic first interest payment found")
                print(f"   Expected first interest: {pledge[2]:,.2f}")
                print(f"   This might be the issue - first interest not auto-created")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_pledge_3_payments()