"""
Fix Pledge 3 by creating the missing automatic first interest payment
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings
from datetime import date

def fix_pledge_3_first_interest():
    """Create missing first interest payment for pledge 3"""
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as db:
            print("🔧 Fixing Pledge 3 First Interest Payment...")
            print("=" * 60)
            
            # Get pledge 3 details
            pledge_result = db.execute(text("""
                SELECT 
                    pledge_id,
                    pledge_no,
                    pledge_date,
                    first_month_interest,
                    final_amount,
                    company_id
                FROM pledges 
                WHERE pledge_id = 3
            """))
            
            pledge = pledge_result.fetchone()
            if not pledge:
                print("❌ Pledge 3 not found!")
                return
                
            pledge_id = pledge[0]
            pledge_no = pledge[1]
            pledge_date = pledge[2]
            first_interest = float(pledge[3])
            final_amount = float(pledge[4])
            company_id = pledge[5]
            
            print(f"📋 Pledge {pledge_no} Details:")
            print(f"   Pledge Date: {pledge_date}")
            print(f"   First Month Interest: {first_interest:,.2f}")
            print(f"   Final Amount: {final_amount:,.2f}")
            
            # Check if first interest payment already exists
            existing_result = db.execute(text("""
                SELECT payment_id, receipt_no 
                FROM pledge_payments 
                WHERE pledge_id = 3 
                AND (payment_type = 'first_interest' OR receipt_no LIKE 'FI-%')
            """))
            
            existing = existing_result.fetchone()
            if existing:
                print(f"✅ First interest payment already exists:")
                print(f"   Payment ID: {existing[0]}")
                print(f"   Receipt: {existing[1]}")
                return
            
            # Generate first interest receipt number
            current_year = pledge_date.year
            fi_count_result = db.execute(text("""
                SELECT COUNT(*) 
                FROM pledge_payments 
                WHERE company_id = :company_id 
                AND receipt_no LIKE :pattern
            """), {
                'company_id': company_id,
                'pattern': f"FI-{company_id}-{current_year}-%"
            })
            
            fi_count = fi_count_result.scalar() or 0
            next_fi_number = fi_count + 1
            fi_receipt_no = f"FI-{company_id}-{current_year}-{next_fi_number:05d}"
            
            print(f"\n🚀 Creating first interest payment:")
            print(f"   Receipt Number: {fi_receipt_no}")
            print(f"   Amount: {first_interest:,.2f}")
            
            # Calculate balance after first interest payment
            balance_after_fi = final_amount - first_interest
            
            # Create the first interest payment
            db.execute(text("""
                INSERT INTO pledge_payments (
                    pledge_id,
                    payment_date,
                    payment_type,
                    amount,
                    interest_amount,
                    principal_amount,
                    penalty_amount,
                    discount_amount,
                    balance_amount,
                    payment_method,
                    receipt_no,
                    remarks,
                    created_by,
                    company_id,
                    created_at
                ) VALUES (
                    :pledge_id,
                    :payment_date,
                    'first_interest',
                    :amount,
                    :interest_amount,
                    0.0,
                    0.0,
                    0.0,
                    :balance_amount,
                    'auto',
                    :receipt_no,
                    'Automatic first month interest payment',
                    1,
                    :company_id,
                    NOW()
                )
            """), {
                'pledge_id': pledge_id,
                'payment_date': pledge_date,
                'amount': first_interest,
                'interest_amount': first_interest,
                'balance_amount': balance_after_fi,
                'receipt_no': fi_receipt_no,
                'company_id': company_id
            })
            
            # Now recalculate the balance for the existing payment (ID 8)
            # Get total payments after adding first interest
            total_result = db.execute(text("""
                SELECT SUM(amount) 
                FROM pledge_payments 
                WHERE pledge_id = 3
            """))
            
            total_payments = float(total_result.scalar() or 0)
            new_balance = final_amount - total_payments
            
            print(f"   Balance after FI: {balance_after_fi:,.2f}")
            print(f"   Total payments now: {total_payments:,.2f}")
            print(f"   New balance: {new_balance:,.2f}")
            
            # Update the existing payment's balance
            db.execute(text("""
                UPDATE pledge_payments 
                SET balance_amount = :new_balance
                WHERE payment_id = 8
            """), {'new_balance': new_balance})
            
            # Update pledge status based on new balance
            if new_balance <= 0.01:  # Allow small floating point errors
                new_status = 'redeemed'
                print(f"   ✅ Pledge should be REDEEMED")
            elif total_payments > first_interest:
                new_status = 'partial_paid'
                print(f"   🔄 Pledge should be PARTIAL_PAID")
            else:
                new_status = 'active'
                print(f"   📋 Pledge should be ACTIVE")
            
            # Update pledge status
            db.execute(text("""
                UPDATE pledges 
                SET status = :new_status 
                WHERE pledge_id = 3
            """), {'new_status': new_status})
            
            db.commit()
            
            print(f"\n🎉 Successfully fixed Pledge 3!")
            print(f"   ✅ Created first interest payment: {fi_receipt_no}")
            print(f"   ✅ Updated existing payment balance: {new_balance:,.2f}")
            print(f"   ✅ Updated pledge status: {new_status}")
            
            if new_balance <= 0.01:
                print(f"   🎊 PLEDGE IS NOW FULLY CLOSED!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_pledge_3_first_interest()