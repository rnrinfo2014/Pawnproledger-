"""
Test Payment Status Update
This script tests payment creation and verifies status updates work correctly
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def test_payment_logic():
    """Test payment creation and status update logic"""
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as db:
            print("🧪 Testing Payment Status Update Logic...")
            print("=" * 60)
            
            # Find a pledge with partial payments that could be closed
            result = db.execute(text("""
                SELECT 
                    p.pledge_id,
                    p.pledge_no,
                    p.final_amount,
                    p.status,
                    COALESCE(SUM(pp.amount), 0) as total_payments,
                    (p.final_amount - COALESCE(SUM(pp.amount), 0)) as remaining_balance
                FROM pledges p
                LEFT JOIN pledge_payments pp ON p.pledge_id = pp.pledge_id
                WHERE p.company_id = 1 
                AND p.status IN ('active', 'partial_paid')
                GROUP BY p.pledge_id, p.pledge_no, p.final_amount, p.status
                HAVING (p.final_amount - COALESCE(SUM(pp.amount), 0)) > 0
                ORDER BY remaining_balance ASC
                LIMIT 3
            """))
            
            pledges = result.fetchall()
            
            if not pledges:
                print("❌ No suitable pledges found for testing")
                return
            
            print("📋 Available pledges for testing:")
            print("-" * 80)
            print(f"{'Pledge No':<12} {'Status':<15} {'Final Amt':<12} {'Paid':<12} {'Balance':<12}")
            print("-" * 80)
            
            for i, pledge in enumerate(pledges):
                pledge_id = pledge[0]
                pledge_no = pledge[1]
                final_amount = float(pledge[2])
                current_status = pledge[3]
                total_payments = float(pledge[4])
                remaining_balance = float(pledge[5])
                
                print(f"{pledge_no:<12} {current_status:<15} {final_amount:<12.2f} {total_payments:<12.2f} {remaining_balance:<12.2f}")
            
            print("-" * 80)
            print("\n💡 To test full payment closure:")
            print("1. Choose a pledge from above")
            print("2. Make a payment equal to the 'Balance' amount")
            print("3. The pledge status should automatically change to 'redeemed'")
            print("\n📝 Example API call:")
            
            # Show example for first pledge
            if pledges:
                example_pledge = pledges[0]
                remaining_balance = float(example_pledge[5])
                
                print(f"""
POST /pledge-payments/
{{
    "pledge_id": {example_pledge[0]},
    "amount": {remaining_balance:.2f},
    "payment_type": "settlement",
    "payment_method": "cash",
    "remarks": "Full settlement payment"
}}
                """)
                
                print(f"✅ After this payment, pledge {example_pledge[1]} should change from '{example_pledge[3]}' to 'redeemed'")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Payment Logic Test...")
    print("=" * 50)
    test_payment_logic()
    print("=" * 50)
    print("✅ Test completed!")