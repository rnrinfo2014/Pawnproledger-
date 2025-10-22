"""
Fix Final Amount Calculation Script
This script corrects the final_amount field for pledges where it's calculated incorrectly
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def fix_final_amounts():
    """Fix incorrect final_amount calculations in pledges"""
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as db:
            print("🔍 Checking final_amount calculations...")
            
            # Get all pledges with their components
            result = db.execute(text("""
                SELECT 
                    pledge_id,
                    pledge_no,
                    total_loan_amount,
                    first_month_interest,
                    document_charges,
                    final_amount,
                    (total_loan_amount + first_month_interest + document_charges) as calculated_final
                FROM pledges 
                WHERE company_id = 1
                ORDER BY pledge_id
            """))
            
            pledges = result.fetchall()
            
            print(f"\n📊 Found {len(pledges)} pledges to check:")
            print("-" * 100)
            
            fixes_needed = []
            
            for pledge in pledges:
                pledge_id = pledge[0]
                pledge_no = pledge[1]
                total_loan = float(pledge[2])
                first_interest = float(pledge[3])
                doc_charges = float(pledge[4])
                current_final = float(pledge[5])
                calculated_final = float(pledge[6])
                
                # Check if final_amount is incorrect (allow for small floating point differences)
                if abs(current_final - calculated_final) > 0.01:
                    fixes_needed.append({
                        'pledge_id': pledge_id,
                        'pledge_no': pledge_no,
                        'current_final': current_final,
                        'calculated_final': calculated_final,
                        'total_loan': total_loan,
                        'first_interest': first_interest,
                        'doc_charges': doc_charges
                    })
                    
                    print(f"❌ {pledge_no}: final_amount = {current_final}, should be {calculated_final}")
                else:
                    print(f"✅ {pledge_no}: final_amount = {current_final} (correct)")
            
            print("-" * 100)
            
            # Apply fixes
            if fixes_needed:
                print(f"\n🔧 Fixing {len(fixes_needed)} incorrect final_amounts...")
                
                for fix in fixes_needed:
                    # Update the final_amount
                    db.execute(text("""
                        UPDATE pledges 
                        SET final_amount = :new_final_amount 
                        WHERE pledge_id = :pledge_id
                    """), {
                        'new_final_amount': fix['calculated_final'],
                        'pledge_id': fix['pledge_id']
                    })
                    
                    print(f"✅ Fixed {fix['pledge_no']}: {fix['current_final']} → {fix['calculated_final']}")
                
                db.commit()
                print(f"\n🎉 Successfully fixed {len(fixes_needed)} final_amount calculations!")
                
                # Now update payment balances based on corrected final amounts
                print("\n🔄 Recalculating payment balances...")
                
                for fix in fixes_needed:
                    # Get total payments for this pledge
                    payment_result = db.execute(text("""
                        SELECT COALESCE(SUM(amount), 0) as total_payments
                        FROM pledge_payments 
                        WHERE pledge_id = :pledge_id
                    """), {'pledge_id': fix['pledge_id']})
                    
                    payment_row = payment_result.fetchone()
                    total_payments = float(payment_row[0]) if payment_row else 0.0
                    new_balance = fix['calculated_final'] - total_payments
                    
                    # Update the balance_amount in the latest payment
                    db.execute(text("""
                        UPDATE pledge_payments 
                        SET balance_amount = :new_balance 
                        WHERE pledge_id = :pledge_id 
                        AND payment_id = (
                            SELECT MAX(payment_id) 
                            FROM pledge_payments 
                            WHERE pledge_id = :pledge_id
                        )
                    """), {
                        'new_balance': new_balance,
                        'pledge_id': fix['pledge_id']
                    })
                    
                    print(f"  Updated balance for {fix['pledge_no']}: {new_balance}")
                
                db.commit()
                print("✅ Payment balances updated!")
                
            else:
                print("\n✅ All final_amount calculations are correct!")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Final Amount Fix...")
    print("=" * 50)
    fix_final_amounts()
    print("=" * 50)
    print("✅ Fix completed!")