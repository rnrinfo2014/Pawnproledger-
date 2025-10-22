"""
Debug Payment Status Update Issue
This script helps debug why pledge status isn't updating to 'redeemed' after full payment
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def debug_payment_status():
    """Debug payment and status update issues"""
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as db:
            print("🔍 Debugging Payment Status Updates...")
            print("=" * 60)
            
            # Get all pledges with their payment details
            result = db.execute(text("""
                SELECT 
                    p.pledge_id,
                    p.pledge_no,
                    p.final_amount,
                    p.status,
                    COALESCE(SUM(pp.amount), 0) as total_payments,
                    (p.final_amount - COALESCE(SUM(pp.amount), 0)) as remaining_balance,
                    COUNT(pp.payment_id) as payment_count
                FROM pledges p
                LEFT JOIN pledge_payments pp ON p.pledge_id = pp.pledge_id
                WHERE p.company_id = 1
                GROUP BY p.pledge_id, p.pledge_no, p.final_amount, p.status
                ORDER BY p.pledge_id
            """))
            
            pledges = result.fetchall()
            
            print(f"📊 Found {len(pledges)} pledges:")
            print("-" * 100)
            print(f"{'Pledge No':<12} {'Status':<15} {'Final Amt':<12} {'Paid':<12} {'Balance':<12} {'Payments':<10} {'Should Be':<15}")
            print("-" * 100)
            
            status_issues = []
            
            for pledge in pledges:
                pledge_id = pledge[0]
                pledge_no = pledge[1]
                final_amount = float(pledge[2])
                current_status = pledge[3]
                total_payments = float(pledge[4])
                remaining_balance = float(pledge[5])
                payment_count = pledge[6]
                
                # Determine what status should be
                if remaining_balance <= 0:
                    expected_status = "redeemed"
                elif total_payments > 0:
                    expected_status = "partial_paid"
                else:
                    expected_status = "active"
                
                # Check for status mismatch
                status_correct = current_status == expected_status
                status_indicator = "✅" if status_correct else "❌"
                
                print(f"{pledge_no:<12} {current_status:<15} {final_amount:<12.2f} {total_payments:<12.2f} {remaining_balance:<12.2f} {payment_count:<10} {expected_status:<15} {status_indicator}")
                
                if not status_correct:
                    status_issues.append({
                        'pledge_id': pledge_id,
                        'pledge_no': pledge_no,
                        'current_status': current_status,
                        'expected_status': expected_status,
                        'final_amount': final_amount,
                        'total_payments': total_payments,
                        'remaining_balance': remaining_balance
                    })
            
            print("-" * 100)
            
            # Show detailed payment information for problematic pledges
            if status_issues:
                print(f"\n🔧 Found {len(status_issues)} status issues to fix:")
                print("=" * 60)
                
                for issue in status_issues:
                    print(f"\n📋 {issue['pledge_no']} (ID: {issue['pledge_id']}):")
                    print(f"   Current Status: {issue['current_status']}")
                    print(f"   Expected Status: {issue['expected_status']}")
                    print(f"   Final Amount: {issue['final_amount']}")
                    print(f"   Total Payments: {issue['total_payments']}")
                    print(f"   Remaining Balance: {issue['remaining_balance']}")
                    
                    # Get payment details for this pledge
                    payment_result = db.execute(text("""
                        SELECT 
                            payment_id,
                            amount,
                            balance_amount,
                            payment_date,
                            remarks
                        FROM pledge_payments 
                        WHERE pledge_id = :pledge_id
                        ORDER BY created_at DESC
                    """), {'pledge_id': issue['pledge_id']})
                    
                    payments = payment_result.fetchall()
                    if payments:
                        print(f"   Recent Payments:")
                        for payment in payments:
                            print(f"     • Payment {payment[0]}: Amount={payment[1]}, Balance={payment[2]}, Date={payment[3]}")
                
                # Ask user if they want to fix the statuses
                print(f"\n🔧 Do you want to fix these status issues? (y/n): ", end="")
                fix_choice = input().lower().strip()
                
                if fix_choice == 'y':
                    print("\n🚀 Fixing status issues...")
                    
                    for issue in status_issues:
                        # Update the pledge status
                        db.execute(text("""
                            UPDATE pledges 
                            SET status = :new_status 
                            WHERE pledge_id = :pledge_id
                        """), {
                            'new_status': issue['expected_status'],
                            'pledge_id': issue['pledge_id']
                        })
                        
                        print(f"✅ Fixed {issue['pledge_no']}: {issue['current_status']} → {issue['expected_status']}")
                    
                    db.commit()
                    print(f"\n🎉 Successfully fixed {len(status_issues)} pledge statuses!")
                else:
                    print("\n⏭️ Skipping status fixes.")
            else:
                print("\n✅ All pledge statuses are correct!")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Payment Status Debug...")
    print("=" * 50)
    debug_payment_status()
    print("=" * 50)
    print("✅ Debug completed!")