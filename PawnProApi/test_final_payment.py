"""
Test script to make a final payment for pledge 3 to demonstrate the automatic status update
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings
from datetime import date

def test_final_payment():
    """Test making final payment to close pledge 3"""
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as db:
            print("🧪 Testing Final Payment for Pledge 3...")
            print("=" * 60)
            
            # Check current status
            result = db.execute(text("""
                SELECT 
                    pledge_no,
                    status,
                    final_amount,
                    COALESCE(SUM(pp.amount), 0) as total_paid,
                    (final_amount - COALESCE(SUM(pp.amount), 0)) as balance
                FROM pledges p
                LEFT JOIN pledge_payments pp ON p.pledge_id = pp.pledge_id
                WHERE p.pledge_id = 3
                GROUP BY p.pledge_id, p.pledge_no, p.status, p.final_amount
            """))
            
            pledge_info = result.fetchone()
            if not pledge_info:
                print("❌ Pledge 3 not found!")
                return
                
            pledge_no = pledge_info[0]
            current_status = pledge_info[1]
            final_amount = float(pledge_info[2])
            total_paid = float(pledge_info[3])
            balance = float(pledge_info[4])
            
            print(f"📋 Current Pledge Status:")
            print(f"   Pledge No: {pledge_no}")
            print(f"   Status: {current_status}")
            print(f"   Final Amount: {final_amount:,.2f}")
            print(f"   Total Paid: {total_paid:,.2f}")
            print(f"   Balance: {balance:,.2f}")
            
            if balance <= 0.01:
                print(f"✅ Pledge is already fully paid!")
                return
                
            print(f"\n🧪 What would happen if you make a payment of {balance:,.2f}?")
            print(f"   New balance would be: {balance - balance:.2f}")
            print(f"   Expected status: redeemed (CLOSED)")
            print(f"   Expected receipt: RCPT-1-2025-00009")
            
            print(f"\n💡 To test this, make a payment API call with:")
            print(f"   {{'pledge_id': 3, 'amount': {balance}, 'payment_type': 'final_payment', 'principal_amount': {balance}}}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_final_payment()