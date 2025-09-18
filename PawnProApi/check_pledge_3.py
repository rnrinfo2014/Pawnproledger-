"""
Check specific pledge status and payment details
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def check_pledge_3():
    """Check pledge ID 3 specifically"""
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as db:
            print("🔍 Checking Pledge ID 3...")
            print("=" * 60)
            
            # Get pledge details
            result = db.execute(text("""
                SELECT 
                    pledge_id,
                    pledge_no,
                    final_amount,
                    status,
                    created_at
                FROM pledges 
                WHERE pledge_id = 3
            """))
            
            pledge = result.fetchone()
            
            if pledge:
                print(f"📋 Pledge Details:")
                print(f"   ID: {pledge[0]}")
                print(f"   Number: {pledge[1]}")
                print(f"   Final Amount: {pledge[2]}")
                print(f"   Current Status: {pledge[3]}")
                print(f"   Created: {pledge[4]}")
                
                # Get all payments for this pledge
                payments_result = db.execute(text("""
                    SELECT 
                        payment_id,
                        amount,
                        balance_amount,
                        payment_date,
                        created_at,
                        remarks
                    FROM pledge_payments 
                    WHERE pledge_id = 3
                    ORDER BY created_at DESC
                """))
                
                payments = payments_result.fetchall()
                
                print(f"\n💰 Payments ({len(payments)} total):")
                total_paid = 0
                for payment in payments:
                    total_paid += float(payment[1])
                    print(f"   • Payment {payment[0]}: {payment[1]} (Balance: {payment[2]}) - {payment[3]} - {payment[5] or 'No remarks'}")
                
                remaining = float(pledge[2]) - total_paid
                print(f"\n📊 Summary:")
                print(f"   Final Amount: {pledge[2]}")
                print(f"   Total Paid: {total_paid}")
                print(f"   Remaining: {remaining}")
                print(f"   Expected Status: {'redeemed' if remaining <= 0.01 else 'partial_paid' if total_paid > 0 else 'active'}")
                print(f"   Actual Status: {pledge[3]}")
                
                # Check if status needs update
                expected_status = 'redeemed' if remaining <= 0.01 else 'partial_paid' if total_paid > 0 else 'active'
                if pledge[3] != expected_status:
                    print(f"\n🔧 Status needs update: {pledge[3]} → {expected_status}")
                    
                    # Update the status
                    db.execute(text("""
                        UPDATE pledges 
                        SET status = :new_status 
                        WHERE pledge_id = 3
                    """), {'new_status': expected_status})
                    
                    db.commit()
                    print(f"✅ Status updated successfully!")
                else:
                    print(f"\n✅ Status is correct!")
                    
            else:
                print("❌ Pledge ID 3 not found!")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_pledge_3()