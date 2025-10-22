"""
Pledge Accounting Manager
Handles complete accounting entries for pledge creation, payments, and settlements
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.core.models import (
    Pledge as PledgeModel, 
    Customer as CustomerModel, 
    PledgePayment as PledgePaymentModel,
    LedgerEntry as LedgerEntryModel,
    MasterAccount as MasterAccountModel,
    VoucherMaster as VoucherMasterModel
)
from typing import Optional
from datetime import date

def create_ledger_entry(
    db: Session,
    voucher_id: Optional[int] = None,
    account_id: Optional[int] = None,
    account_code: Optional[str] = None,
    debit: float = 0.0,
    credit: float = 0.0,
    description: str = "",
    reference_type: Optional[str] = None,
    reference_id: Optional[int] = None,
    transaction_date: Optional[date] = None,
    company_id: int = 1
) -> LedgerEntryModel:
    """
    Create a ledger entry for accounting transactions
    
    Args:
        db: Database session
        voucher_id: Voucher ID to link this entry to
        account_id: Direct account ID (for customer accounts)
        account_code: Account code to lookup (for standard accounts)
        debit: Debit amount
        credit: Credit amount
        description: Transaction description
        reference_type: Type of reference ('pledge', 'payment', etc.)
        reference_id: ID of the referenced record
        transaction_date: Business transaction date
        company_id: Company ID
        
    Returns:
        Created LedgerEntry instance
    """
    
    # Determine account ID
    if account_id:
        target_account_id = account_id
    elif account_code:
        account = db.query(MasterAccountModel).filter(
            MasterAccountModel.account_code == account_code,
            MasterAccountModel.company_id == company_id
        ).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account with code {account_code} not found"
            )
        target_account_id = account.account_id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either account_id or account_code must be provided"
        )
    
    # Validate debit/credit
    if debit < 0 or credit < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debit and credit amounts must be positive"
        )
    
    if debit > 0 and credit > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot have both debit and credit in the same entry"
        )
    
    if debit == 0 and credit == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either debit or credit must be greater than zero"
        )
    
    # Create ledger entry
    ledger_entry = LedgerEntryModel(
        voucher_id=voucher_id,
        account_id=target_account_id,
        debit=debit,
        credit=credit,
        dr_cr='D' if debit > 0 else 'C',
        amount=debit if debit > 0 else credit,
        description=description,
        narration=description[:255] if description else "",  # Legacy field
        reference_type=reference_type,
        reference_id=reference_id,
        transaction_date=transaction_date or date.today(),
        entry_date=transaction_date or date.today(),  # Legacy field
        company_id=company_id
    )
    
    db.add(ledger_entry)
    db.flush()
    
    return ledger_entry

def create_complete_pledge_accounting(
    db: Session, 
    pledge: PledgeModel, 
    customer: CustomerModel, 
    first_payment: Optional[PledgePaymentModel] = None
) -> dict:
    """
    Create complete accounting entries for pledge creation
    
    Args:
        db: Database session
        pledge: Pledge model instance
        customer: Customer model instance  
        first_payment: First interest payment (if any)
        
    Returns:
        Dictionary with created ledger entry IDs
    """
    
    if not customer.coa_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer {customer.name} does not have a COA account"
        )
    
    created_entries = []
    
    try:
        # Create a voucher for this pledge transaction
        voucher = VoucherMasterModel(
            voucher_date=pledge.pledge_date,
            voucher_type="Pledge",
            narration=f"Pledge {pledge.pledge_no} - Initial transaction",
            company_id=pledge.company_id,
            created_by=pledge.created_by
        )
        db.add(voucher)
        db.flush()  # Get the voucher_id
        
        # Entry 1: Record pledged ornaments and customer liability
        entry1_dr = create_ledger_entry(
            db=db,
            voucher_id=voucher.voucher_id,
            account_code="1005",  # Pledged Ornaments
            debit=pledge.total_loan_amount,
            credit=0,
            description=f"Pledge {pledge.pledge_no} - Ornaments received from {customer.name}",
            reference_type="pledge",
            reference_id=pledge.pledge_id,
            transaction_date=pledge.pledge_date,
            company_id=pledge.company_id
        )
        created_entries.append(entry1_dr.entry_id)
        
        entry1_cr = create_ledger_entry(
            db=db,
            voucher_id=voucher.voucher_id,
            account_id=customer.coa_account_id,  # Individual customer account
            debit=0,
            credit=pledge.total_loan_amount,
            description=f"Pledge {pledge.pledge_no} - Initial loan liability",
            reference_type="pledge",
            reference_id=pledge.pledge_id,
            transaction_date=pledge.pledge_date,
            company_id=pledge.company_id
        )
        created_entries.append(entry1_cr.entry_id)
        
        # Entry 2: Document charges (if any)
        if pledge.document_charges and pledge.document_charges > 0:
            entry2_dr = create_ledger_entry(
                db=db,
                voucher_id=voucher.voucher_id,
                account_id=customer.coa_account_id,
                debit=pledge.document_charges,
                credit=0,
                description=f"Pledge {pledge.pledge_no} - Document charges",
                reference_type="pledge",
                reference_id=pledge.pledge_id,
                transaction_date=pledge.pledge_date,
                company_id=pledge.company_id
            )
            created_entries.append(entry2_dr.entry_id)
            
            entry2_cr = create_ledger_entry(
                db=db,
                voucher_id=voucher.voucher_id,
                account_code="4003",  # Service Charges
                debit=0,
                credit=pledge.document_charges,
                description=f"Pledge {pledge.pledge_no} - Document charges income",
                reference_type="pledge",
                reference_id=pledge.pledge_id,
                transaction_date=pledge.pledge_date,
                company_id=pledge.company_id
            )
            created_entries.append(entry2_cr.entry_id)
        
        # Entry 3: First month interest received (if payment exists)
        if first_payment and first_payment.interest_amount > 0:
            entry3_dr = create_ledger_entry(
                db=db,
                voucher_id=voucher.voucher_id,
                account_code="1001",  # Cash in Hand
                debit=first_payment.interest_amount,
                credit=0,
                description=f"Pledge {pledge.pledge_no} - First month interest received",
                reference_type="payment",
                reference_id=first_payment.payment_id,
                transaction_date=first_payment.payment_date,
                company_id=pledge.company_id
            )
            created_entries.append(entry3_dr.entry_id)
            
            entry3_cr = create_ledger_entry(
                db=db,
                voucher_id=voucher.voucher_id,
                account_id=customer.coa_account_id,
                debit=0,
                credit=first_payment.interest_amount,
                description=f"Pledge {pledge.pledge_no} - First month interest",
                reference_type="payment",
                reference_id=first_payment.payment_id,
                transaction_date=first_payment.payment_date,
                company_id=pledge.company_id
            )
            created_entries.append(entry3_cr.entry_id)
        
        print(f"✅ Created {len(created_entries)} ledger entries for pledge {pledge.pledge_no}")
        
        return {
            "success": True,
            "pledge_id": pledge.pledge_id,
            "pledge_no": pledge.pledge_no,
            "customer_name": customer.name,
            "ledger_entries_created": len(created_entries),
            "ledger_entry_ids": created_entries,
            "total_loan_amount": pledge.total_loan_amount,
            "document_charges": pledge.document_charges or 0,
            "first_interest": first_payment.interest_amount if first_payment else 0,
            "net_customer_liability": (
                pledge.total_loan_amount - 
                (pledge.document_charges or 0) - 
                (first_payment.interest_amount if first_payment else 0)
            )
        }
        
    except Exception as e:
        # Clean up any created entries if error occurs
        if created_entries:
            db.query(LedgerEntryModel).filter(
                LedgerEntryModel.entry_id.in_(created_entries)
            ).delete(synchronize_session=False)
        
        # Log the full error with traceback
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"ERROR in create_complete_pledge_accounting: {error_msg}")
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pledge accounting entries: {error_msg}"
        )

def get_customer_balance_from_ledger(db: Session, customer_id: int) -> dict:
    """
    Calculate customer balance from ledger entries
    
    Args:
        db: Database session
        customer_id: Customer ID
        
    Returns:
        Dictionary with balance information
    """
    
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if not customer.coa_account_id:
        return {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "balance": 0.0,
            "has_coa_account": False,
            "transaction_count": 0
        }
    
    # Calculate balance from ledger entries
    # For liability accounts: Credit increases liability, Debit decreases liability
    # Positive balance = Customer owes us money
    from sqlalchemy import func
    
    ledger_summary = db.query(
        func.sum(LedgerEntryModel.credit - LedgerEntryModel.debit).label('balance'),
        func.count(LedgerEntryModel.entry_id).label('transaction_count')
    ).filter(
        LedgerEntryModel.account_id == customer.coa_account_id
    ).first()
    
    balance = float(ledger_summary.balance) if ledger_summary.balance else 0.0
    transaction_count = ledger_summary.transaction_count or 0
    
    return {
        "customer_id": customer_id,
        "customer_name": customer.name,
        "balance": balance,
        "has_coa_account": True,
        "account_code": customer.coa_account.account_code if customer.coa_account else None,
        "transaction_count": transaction_count,
        "balance_interpretation": "Customer owes us" if balance > 0 else "We owe customer" if balance < 0 else "Zero balance"
    }

def validate_pledge_accounting_balance(db: Session, pledge_id: int) -> dict:
    """
    Validate that accounting entries for a pledge are balanced
    
    Args:
        db: Database session
        pledge_id: Pledge ID to validate
        
    Returns:
        Dictionary with validation results
    """
    
    # Get all ledger entries for this pledge
    pledge_entries = db.query(LedgerEntryModel).filter(
        LedgerEntryModel.reference_type == "pledge",
        LedgerEntryModel.reference_id == pledge_id
    ).all()
    
    payment_entries = db.query(LedgerEntryModel).filter(
        LedgerEntryModel.reference_type == "payment",
        LedgerEntryModel.reference_id.in_(
            db.query(PledgePaymentModel.payment_id).filter(
                PledgePaymentModel.pledge_id == pledge_id
            )
        )
    ).all()
    
    all_entries = pledge_entries + payment_entries
    
    total_debits = sum(entry.debit for entry in all_entries)
    total_credits = sum(entry.credit for entry in all_entries)
    
    is_balanced = abs(total_debits - total_credits) < 0.01  # Allow for minor rounding differences
    
    return {
        "pledge_id": pledge_id,
        "total_entries": len(all_entries),
        "pledge_entries": len(pledge_entries),
        "payment_entries": len(payment_entries),
        "total_debits": total_debits,
        "total_credits": total_credits,
        "difference": total_debits - total_credits,
        "is_balanced": is_balanced,
        "validation_status": "PASSED" if is_balanced else "FAILED"
    }

def create_payment_accounting(
    db: Session,
    payment: PledgePaymentModel,
    pledge: PledgeModel,
    customer: CustomerModel,
    company_id: int
) -> dict:
    """
    Create complete accounting entries for a pledge payment
    
    This function creates proper double-entry bookkeeping for pledge payments:
    1. Cash/Bank Dr. (amount received)
    2. Customer Account Cr. (reducing customer's debt to us)
    3. Interest Income Cr. (if interest portion)
    4. Penalty Income Cr. (if penalty portion)
    
    Args:
        db: Database session
        payment: PledgePayment record
        pledge: Pledge record
        customer: Customer record
        company_id: Company ID
        
    Returns:
        Dictionary with accounting summary
    """
    
    try:
        # Create voucher for this payment
        voucher = VoucherMasterModel(
            voucher_date=payment.payment_date,
            voucher_type='Payment',
            narration=f"Payment received for Pledge {pledge.pledge_no} from {customer.name}",
            created_by=payment.created_by,
            company_id=company_id
        )
        db.add(voucher)
        db.flush()  # Get voucher ID
        
        # Verify customer has COA account
        if not customer.coa_account_id:
            raise HTTPException(
                status_code=400,
                detail=f"Customer {customer.name} does not have a COA account. Please contact administrator."
            )
        
        entries_created = []
        
        # Entry 1: Cash/Bank Account Dr. (Cash/Bank increased - asset increased)
        # Determine payment method account
        if payment.payment_method == 'bank' or payment.bank_reference:
            # Bank payment - find bank cash account
            bank_account = db.query(MasterAccountModel).filter(
                MasterAccountModel.account_code.like("1002%"),  # Bank accounts
                MasterAccountModel.company_id == company_id
            ).first()
            cash_account = bank_account
        else:
            # Cash payment - find cash account  
            cash_account = db.query(MasterAccountModel).filter(
                MasterAccountModel.account_code == "1001",  # Cash account
                MasterAccountModel.company_id == company_id
            ).first()
            
        if not cash_account:
            # Fallback to first available cash account
            cash_account = db.query(MasterAccountModel).filter(
                MasterAccountModel.account_code.like("100%"),  # Any cash/bank account
                MasterAccountModel.company_id == company_id
            ).first()
            
        if not cash_account:
            raise HTTPException(
                status_code=500,
                detail="No cash/bank account found in chart of accounts"
            )
        
        cash_entry = create_ledger_entry(
            db=db,
            voucher_id=voucher.voucher_id,
            account_code=cash_account.account_code,
            debit=payment.amount,
            credit=0.0,
            description=f"Payment received from {customer.name} for Pledge {pledge.pledge_no}",
            reference_type="payment",
            reference_id=payment.payment_id,
            transaction_date=payment.payment_date,
            company_id=company_id
        )
        entries_created.append(cash_entry)
        
        # Entry 2: Customer Account Cr. (Customer debt reduced - liability reduced)
        customer_entry = create_ledger_entry(
            db=db,
            voucher_id=voucher.voucher_id,
            account_id=customer.coa_account_id,
            debit=0.0,
            credit=payment.amount,
            description=f"Payment received for Pledge {pledge.pledge_no}",
            reference_type="payment",
            reference_id=payment.payment_id,
            transaction_date=payment.payment_date,
            company_id=company_id
        )
        entries_created.append(customer_entry)
        
        # Optional: Split between interest, principal, penalty, and discount if specified
        interest_amount = getattr(payment, 'interest_amount', 0.0) or 0.0
        penalty_amount = getattr(payment, 'penalty_amount', 0.0) or 0.0
        discount_amount = getattr(payment, 'discount_amount', 0.0) or 0.0
        
        # Entry 3: Interest Income (if any)
        if interest_amount > 0:
            interest_account = db.query(MasterAccountModel).filter(
                MasterAccountModel.account_code.like("4002%"),  # Interest Income
                MasterAccountModel.company_id == company_id
            ).first()
            
            if interest_account:
                # Adjust customer credit entry
                customer_entry.credit = customer_entry.credit - interest_amount
                
                # Create interest income entry
                interest_entry = create_ledger_entry(
                    db=db,
                    voucher_id=voucher.voucher_id,
                    account_code=interest_account.account_code,
                    debit=0.0,
                    credit=interest_amount,
                    description=f"Interest income for Pledge {pledge.pledge_no}",
                    reference_type="payment",
                    reference_id=payment.payment_id,
                    transaction_date=payment.payment_date,
                    company_id=company_id
                )
                entries_created.append(interest_entry)
        
        # Entry 4: Penalty Income (if any)
        if penalty_amount > 0:
            penalty_account = db.query(MasterAccountModel).filter(
                MasterAccountModel.account_code.like("4003%"),  # Penalty Income
                MasterAccountModel.company_id == company_id
            ).first()
            
            if penalty_account:
                # Adjust customer credit entry further
                customer_entry.credit = customer_entry.credit - penalty_amount
                
                # Create penalty income entry
                penalty_entry = create_ledger_entry(
                    db=db,
                    voucher_id=voucher.voucher_id,
                    account_code=penalty_account.account_code,
                    debit=0.0,
                    credit=penalty_amount,
                    description=f"Penalty income for Pledge {pledge.pledge_no}",
                    reference_type="payment",
                    reference_id=payment.payment_id,
                    transaction_date=payment.payment_date,
                    company_id=company_id
                )
                entries_created.append(penalty_entry)
        
        # Entry 5: Discount Expense (if any)
        if discount_amount > 0:
            discount_account = db.query(MasterAccountModel).filter(
                MasterAccountModel.account_code == "5008",  # Customer Discount Account
                MasterAccountModel.company_id == company_id
            ).first()
            
            if not discount_account:
                # Try alternative discount expense account codes
                discount_account = db.query(MasterAccountModel).filter(
                    MasterAccountModel.account_code.in_(["5008", "5030", "6003", "5999"]),  # Various discount account codes
                    MasterAccountModel.company_id == company_id
                ).first()
            
            if discount_account:
                # Adjust customer credit entry to add discount (increasing customer credit for the discount given)
                customer_entry.credit = customer_entry.credit + discount_amount
                
                # Create discount expense entry (debit - expense increased)
                discount_entry = create_ledger_entry(
                    db=db,
                    voucher_id=voucher.voucher_id,
                    account_code=discount_account.account_code,
                    debit=discount_amount,
                    credit=0.0,
                    description=f"Discount given for Pledge {pledge.pledge_no} - {getattr(payment, 'remarks', 'Customer discount')}",
                    reference_type="payment",
                    reference_id=payment.payment_id,
                    transaction_date=payment.payment_date,
                    company_id=company_id
                )
                entries_created.append(discount_entry)
        
        # Verify accounting balance
        total_debits = sum(entry.debit for entry in entries_created)
        total_credits = sum(entry.credit for entry in entries_created)
        
        if abs(total_debits - total_credits) > 0.01:
            raise HTTPException(
                status_code=500,
                detail=f"Accounting entries not balanced. Debits: {total_debits}, Credits: {total_credits}"
            )
        
        return {
            "voucher_id": voucher.voucher_id,
            "entries_created": len(entries_created),
            "total_debits": total_debits,
            "total_credits": total_credits,
            "is_balanced": True,
            "customer_account_id": customer.coa_account_id,
            "payment_method_account": cash_account.account_code,
            "breakdown": {
                "cash_debit": payment.amount,
                "customer_credit": customer_entry.credit,
                "interest_credit": interest_amount,
                "penalty_credit": penalty_amount,
                "discount_debit": discount_amount,
                "principal_amount": payment.amount - interest_amount - penalty_amount,
                "net_customer_impact": customer_entry.credit  # Actual customer account impact after all adjustments
            }
        }
        
    except Exception as e:
        # Rollback will be handled by calling function
        raise HTTPException(
            status_code=500,
            detail=f"Error creating payment accounting: {str(e)}"
        )