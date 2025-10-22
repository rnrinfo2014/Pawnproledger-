"""
Pledge Status Update Verification and Fix Script
This script checks pledge payments and updates status correctly
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def check_and_fix_pledge_status():
    """Check and fix pledge status based on actual payments"""
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as db:
            print("🔍 Checking pledge status updates...")
            
            # Get all pledges with their payment totals
            result = db.execute(text("""
                SELECT 
                    p.pledge_id,
                    p.pledge_no,
                    p.status as current_status,
                    p.final_amount,
                    p.total_loan_amount,
                    p.first_month_interest,
                    p.document_charges,
                    COALESCE(SUM(pay.amount), 0) as total_payments,
                    (p.final_amount - COALESCE(SUM(pay.amount), 0)) as calculated_balance
                FROM pledges p
                LEFT JOIN pledge_payments pay ON p.pledge_id = pay.pledge_id
                WHERE p.company_id = 1
                GROUP BY p.pledge_id, p.pledge_no, p.status, p.final_amount, 
                         p.total_loan_amount, p.first_month_interest, p.document_charges
                ORDER BY p.pledge_id
            """))
            
            pledges = result.fetchall()
            
            print(f"\n📊 Found {len(pledges)} pledges to check:")
            print("-" * 100)
            
            status_updates = []
            
            for pledge in pledges:
                pledge_id = pledge[0]
                pledge_no = pledge[1]
                current_status = pledge[2]
                final_amount = float(pledge[3])
                total_loan = float(pledge[4])
                first_interest = float(pledge[5])
                doc_charges = float(pledge[6])
                total_payments = float(pledge[7])
                calculated_balance = float(pledge[8])
                
                # Calculate what final_amount should be
                expected_final = total_loan + first_interest + doc_charges
                final_amount_issue = abs(final_amount - expected_final) > 0.01
                
                # Determine correct status
                if calculated_balance <= 0:
                    correct_status = "redeemed"
                elif total_payments > 0:
                    correct_status = "partial_paid"
                else:
                    correct_status = "active"
                
                status_needs_update = current_status != correct_status
                
                print(f"Pledge {pledge_no} (ID: {pledge_id}):")
                print(f"  Current Status: {current_status}")
                print(f"  Final Amount: {final_amount} {'❌ (Expected: ' + str(expected_final) + ')' if final_amount_issue else '✅'}")
                print(f"  Total Payments: {total_payments}")
                print(f"  Calculated Balance: {calculated_balance}")
                print(f"  Correct Status: {correct_status} {'❌ (Needs Update)' if status_needs_update else '✅'}")
                
                if status_needs_update:
                    status_updates.append({
                        'pledge_id': pledge_id,
                        'pledge_no': pledge_no,
                        'current_status': current_status,
                        'correct_status': correct_status,
                        'balance': calculated_balance
                    })
                
                print("-" * 100)
            
            # Apply status updates
            if status_updates:
                print(f"\n🔧 Applying {len(status_updates)} status updates...")
                
                for update in status_updates:
                    db.execute(text("""
                        UPDATE pledges 
                        SET status = :new_status 
                        WHERE pledge_id = :pledge_id
                    """), {
                        'new_status': update['correct_status'],
                        'pledge_id': update['pledge_id']
                    })
                    
                    print(f"✅ Updated {update['pledge_no']}: {update['current_status']} → {update['correct_status']}")
                
                db.commit()
                print(f"\n🎉 Successfully updated {len(status_updates)} pledge statuses!")
            else:
                print("\n✅ All pledge statuses are correct!")
                
            # Show final status summary
            print("\n📈 Final Status Summary:")
            final_result = db.execute(text("""
                SELECT status, COUNT(*) as count
                FROM pledges 
                WHERE company_id = 1
                GROUP BY status
                ORDER BY status
            """))
            
            for row in final_result:
                status = row[0]
                count = row[1]
                status_display = {
                    'active': 'ACTIVE (No payments)',
                    'partial_paid': 'ACTIVE (Partial payments)', 
                    'redeemed': 'CLOSED (Fully paid)'
                }.get(status, status.upper())
                print(f"  {status_display}: {count} pledges")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Pledge Status Verification...")
    print("=" * 50)
    check_and_fix_pledge_status()
    print("=" * 50)
    print("✅ Verification completed!")