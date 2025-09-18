# type: ignore
# pylint: disable=all
# mypy: ignore-errors
"""
PawnSoft API - Main FastAPI application
This file contains all the API endpoints for the PawnSoft system
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.functions import func
from typing import Generator, List, Optional, Union
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import os
import shutil
from pathlib import Path

from database import SessionLocal, get_db
from auth import authenticate_user, create_access_token, Token, get_current_user, get_current_admin_user, get_password_hash, validate_password
from models import Company as CompanyModel, User as UserModel, MasterAccount as MasterAccountModel, VoucherMaster as VoucherMasterModel, LedgerEntry as LedgerEntryModel, Area as AreaModel, GoldSilverRate as GoldSilverRateModel, JewellDesign as JewellDesignModel, JewellCondition as JewellConditionModel, Scheme as SchemeModel, Customer as CustomerModel, Item as ItemModel, Pledge as PledgeModel, PledgeItem as PledgeItemModel, JewellType as JewellTypeModel, JewellRate as JewellRateModel, Bank as BankModel, PledgePayment as PledgePaymentModel
from config import settings
from security_middleware import SecurityHeadersMiddleware, RateLimitMiddleware, SecurityLoggingMiddleware

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production else None
)

# Add security middleware (order matters!)
if settings.enable_security_headers:
    app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    RateLimitMiddleware, 
    max_requests=settings.rate_limit_requests,
    time_window=settings.rate_limit_period
)

app.add_middleware(SecurityLoggingMiddleware)

# Add CORS middleware with configurable origins
cors_origins = settings.cors_origins_list
# In development, be more permissive with CORS
if settings.environment == "development":
    cors_origins = ["*"]  # Allow all origins in development
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Include OPTIONS for preflight
    allow_headers=["*"],  # Allows all headers
)

# Mount static files for uploads with configurable directory
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Startup event to log configuration
@app.on_event("startup")
async def startup_event():
    print("🚀 PawnSoft API Starting Up...")
    print(f"📍 Environment: {settings.environment}")
    print(f"🌐 CORS Origins: {settings.cors_origins}")
    print(f"🔒 Security Headers: {'Enabled' if settings.enable_security_headers else 'Disabled'}")
    print(f"⚡ Rate Limiting: {settings.rate_limit_requests} requests per {settings.rate_limit_period}s")
    print("✅ API Ready!")

# Import API routers
from coa_api import router as coa_router
from daybook_api import router as daybook_router

# Pydantic models
from pydantic import BaseModel, Field
from typing import Optional

class LedgerTransactionBase(BaseModel):
    account_id: int
    transaction_type: str
    transaction_date: date
    account_code: Optional[str] = None
    narration: Optional[str] = None
    credit: Optional[float] = 0.0
    debit: Optional[float] = 0.0
    company_id: int
    created_by: int
    reference_table: Optional[str] = None
    reference_id: Optional[int] = None

class LedgerTransactionCreate(LedgerTransactionBase):
    pass

class LedgerTransaction(LedgerTransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for MasterAccount
class MasterAccountBase(BaseModel):
    account_name: str
    account_code: str
    parent_id: Optional[int] = None
    account_type: str
    group_name: Optional[str] = None
    is_active: Optional[bool] = True
    company_id: int

class MasterAccountCreate(MasterAccountBase):
    pass

class MasterAccount(MasterAccountBase):
    account_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for VoucherMaster
class VoucherMasterBase(BaseModel):
    voucher_type: str
    voucher_date: date
    narration: Optional[str] = None
    created_by: int
    company_id: int

class VoucherMasterCreate(VoucherMasterBase):
    pass

class VoucherMaster(VoucherMasterBase):
    voucher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for LedgerEntry
class LedgerEntryBase(BaseModel):
    voucher_id: int
    account_id: int
    dr_cr: str
    amount: float
    narration: Optional[str] = None
    entry_date: date

class LedgerEntryCreate(LedgerEntryBase):
    pass

class LedgerEntry(LedgerEntryBase):
    entry_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for Company
class CompanyBase(BaseModel):
    name: str
    address: str
    city: Optional[str] = None
    phone_number: Optional[str] = None
    logo: Optional[str] = None
    license_no: Optional[str] = None
    status: Optional[str] = "active"
    financial_year_start: date
    financial_year_end: date

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for User
class UserBase(BaseModel):
    username: str
    email: str
    role: Optional[str] = "user"
    company_id: int

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for Area
class AreaBase(BaseModel):
    name: str
    status: Optional[str] = "active"
    company_id: int

class AreaCreate(AreaBase):
    pass

class Area(AreaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for GoldSilverRate
class GoldSilverRateBase(BaseModel):
    date: date
    gold_rate_per_gram: float
    silver_rate_per_gram: float
    company_id: int
    created_by: int

class GoldSilverRateCreate(GoldSilverRateBase):
    pass

class GoldSilverRate(GoldSilverRateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for JewellDesign
class JewellDesignBase(BaseModel):
    design_name: str
    status: Optional[str] = "active"

class JewellDesignCreate(JewellDesignBase):
    pass

class JewellDesign(JewellDesignBase):
    id: int
    created_at: datetime

class Config:
    from_attributes = True

# Pydantic models for JewellCondition
class JewellConditionBase(BaseModel):
    condition: str
    status: Optional[str] = "active"

class JewellConditionCreate(JewellConditionBase):
    pass

class JewellCondition(JewellConditionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for JewellType
class JewellTypeBase(BaseModel):
    type_name: str
    status: Optional[str] = "active"

class JewellTypeCreate(JewellTypeBase):
    pass

class JewellType(JewellTypeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for JewellRate
class JewellRateBase(BaseModel):
    date: date
    jewell_type_id: int
    rate: float
    created_by: int

class JewellRateCreate(JewellRateBase):
    pass

class JewellRate(JewellRateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for Scheme
class SchemeBase(BaseModel):
    jewell_category: str
    jewell_type_id: Optional[int] = None  # Foreign key to JewellType
    scheme_name: str
    prefix: Optional[str] = None
    interest_rate_monthly: float
    duration: int
    loan_allowed_percent: float
    slippage_percent: float
    status: Optional[str] = "active"
    acc_code: Optional[str] = None
    company_id: int

class SchemeCreate(SchemeBase):
    pass

class Scheme(SchemeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for Customer
class CustomerBase(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    area_id: Optional[int] = None
    phone: str
    acc_code: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_image: Optional[str] = None
    status: Optional[str] = "active"
    company_id: int
    created_by: int

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for Item
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    weight: Optional[float] = None
    estimated_value: Optional[float] = None
    photos: Optional[str] = None
    customer_id: int
    scheme_id: int
    company_id: int
    status: Optional[str] = "pawned"

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pydantic models for Pledge
class PledgeBase(BaseModel):
    customer_id: int
    scheme_id: int
    pledge_date: date
    due_date: date
    item_count: int
    gross_weight: float
    net_weight: float
    document_charges: Optional[float] = 0.0
    first_month_interest: float
    total_loan_amount: float
    final_amount: float
    status: Optional[str] = "active"
    is_move_to_bank: Optional[bool] = False
    remarks: Optional[str] = None
    company_id: int

class PledgeCreate(PledgeBase):
    pass

class Pledge(PledgeBase):
    pledge_id: int
    pledge_no: str
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True

# Pledge listing schema with required fields
class PledgeOut(BaseModel):
    id: int  # Maps to pledge_id
    pledge_no:str
    customer_id: int
    scheme_id: int
    principal_amount: float  # Maps to total_loan_amount
    interest_rate: float  # Will be calculated from scheme
    start_date: date  # Maps to pledge_date
    maturity_date: date  # Maps to due_date
    remaining_principal: float  # Will be calculated from payments
    status: str  # Maps to status with uppercase conversion
    created_at: datetime
    closed_at: Optional[datetime] = None  # Will be calculated based on status

    class Config:
        from_attributes = True

# Pydantic models for PledgeItem
class PledgeItemBase(BaseModel):
    pledge_id: int
    jewell_design_id: int
    jewell_condition: str
    gross_weight: float
    net_weight: float
    image: Optional[str] = None
    net_value: float
    remarks: Optional[str] = None

class PledgeItemCreate(PledgeItemBase):
    pass

class PledgeItem(PledgeItemBase):
    pledge_item_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Comprehensive Pydantic models for detailed pledge view
class CustomerDetail(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    area_id: Optional[int] = None
    phone: Optional[str] = None  # Your actual field is 'phone', not 'mobile'
    acc_code: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_image: Optional[str] = None  # Your actual field is 'id_image', not 'id_proof'
    status: Optional[str] = None
    created_at: datetime

    # Helper properties for backward compatibility and easy access
    @property
    def mobile(self) -> Optional[str]:
        """Alias for phone field for backward compatibility"""
        return self.phone
    
    @property
    def id_proof(self) -> Optional[str]:
        """Alias for id_image field for backward compatibility"""
        return self.id_image
    
    @property
    def id_proof_url(self) -> Optional[str]:
        """Generate URL for ID proof image"""
        if self.id_image:
            return f"/uploads/{self.id_image}"
        return None

    class Config:
        from_attributes = True

class SchemeDetail(BaseModel):
    id: int
    scheme_name: str
    prefix: Optional[str] = None
    jewell_category: str
    interest_rate_monthly: float
    duration: int
    loan_allowed_percent: float
    slippage_percent: Optional[float] = None

    class Config:
        from_attributes = True

class JewellDesignDetail(BaseModel):
    id: int
    design_name: str
    design_category: Optional[str] = None  # This field exists in your response
    status: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PledgeItemDetail(BaseModel):
    pledge_item_id: int
    jewell_design_id: int
    jewell_design: JewellDesignDetail
    jewell_condition: str
    gross_weight: float
    net_weight: float
    image: Optional[str] = None
    net_value: float
    remarks: Optional[str] = None
    created_at: datetime
    
    # Helper property for image URL
    @property
    def image_url(self) -> Optional[str]:
        if self.image:
            return f"/uploads/{self.image}"
        return None

    class Config:
        from_attributes = True

class UserDetail(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None  # This field appears in your response
    email: Optional[str] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True

class PledgeDetailView(BaseModel):
    # Basic pledge information
    pledge_id: int
    pledge_no: str
    pledge_date: date
    due_date: date
    item_count: int
    gross_weight: float
    net_weight: float
    document_charges: float
    first_month_interest: float
    total_loan_amount: float
    final_amount: float
    status: str
    is_move_to_bank: bool
    remarks: Optional[str] = None
    created_at: datetime
    
    # Related entities with full details
    customer: CustomerDetail
    scheme: SchemeDetail
    user: UserDetail  # Use 'user' to match SQLAlchemy relationship name
    pledge_items: List[PledgeItemDetail]
    
    # Computed properties
    @property
    def total_items(self) -> int:
        return len(self.pledge_items)
    
    @property
    def has_images(self) -> bool:
        return any(item.image for item in self.pledge_items)
    
    @property
    def items_with_images(self) -> List[PledgeItemDetail]:
        return [item for item in self.pledge_items if item.image]

    class Config:
        from_attributes = True
        populate_by_name = True


# ===============================================
# COMPREHENSIVE PLEDGE UPDATE MODELS
# ===============================================

# Customer update model - for partial customer information changes
class CustomerUpdateData(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    area_id: Optional[int] = None
    phone: Optional[str] = None
    id_proof_type: Optional[str] = None
    # Note: id_image updates should be handled through file upload endpoints

class PledgeItemOperation(BaseModel):
    operation: str = Field(..., description="'add', 'update', or 'remove'")
    pledge_item_id: Optional[int] = Field(None, description="Required for 'update' and 'remove' operations")
    jewell_design_id: Optional[int] = Field(None, description="Required for 'add' and 'update' operations")
    jewell_condition: Optional[str] = None
    gross_weight: Optional[float] = None
    net_weight: Optional[float] = None
    net_value: Optional[float] = None
    remarks: Optional[str] = None
    # Note: image updates should be handled through separate file upload endpoints

class PledgeComprehensiveUpdate(BaseModel):
    # Basic pledge information updates
    scheme_id: Optional[int] = Field(None, description="Change to different scheme")
    pledge_date: Optional[date] = Field(None, description="Change pledge date")
    due_date: Optional[date] = Field(None, description="Change due date")
    document_charges: Optional[float] = None
    first_month_interest: Optional[float] = None
    total_loan_amount: Optional[float] = None
    final_amount: Optional[float] = None
    status: Optional[str] = Field(None, description="Change pledge status: 'active', 'redeemed', 'auctioned', etc.")
    is_move_to_bank: Optional[bool] = None
    remarks: Optional[str] = None
    
    # Customer information updates (optional)
    customer_updates: Optional[CustomerUpdateData] = Field(None, description="Update customer information")
    change_customer_id: Optional[int] = Field(None, description="Transfer pledge to different customer entirely")
    
    # Pledge items operations
    item_operations: Optional[List[PledgeItemOperation]] = Field(default_factory=list, description="List of operations to perform on pledge items")
    
    # Financial recalculation flags
    recalculate_weights: Optional[bool] = Field(True, description="Automatically recalculate gross/net weights from items")
    recalculate_item_count: Optional[bool] = Field(True, description="Automatically recalculate item count from items")
    recalculate_financials: Optional[bool] = Field(False, description="Recalculate loan amounts based on new scheme/weights")

class PledgeUpdateResponse(BaseModel):
    success: bool
    message: str
    updated_pledge: PledgeDetailView
    warnings: Optional[List[str]] = Field(default_factory=list, description="Non-critical warnings during update")
    
    # Update summary
    changes_summary: Optional[dict] = Field(default_factory=dict, description="Summary of what was changed")
    items_added: Optional[int] = 0
    items_updated: Optional[int] = 0
    items_removed: Optional[int] = 0


# ===============================================
# BANK MODELS
# ===============================================

# Pydantic models for Bank
class BankBase(BaseModel):
    bank_name: str = Field(..., max_length=200, description="Name of the bank")
    branch_name: Optional[str] = Field(None, max_length=200, description="Branch name")
    account_name: Optional[str] = Field(None, max_length=200, description="Account holder name")
    status: Optional[str] = Field("active", description="Bank status: active, inactive")

class BankCreate(BankBase):
    pass

class BankUpdate(BaseModel):
    bank_name: Optional[str] = Field(None, max_length=200)
    branch_name: Optional[str] = Field(None, max_length=200)
    account_name: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, description="Bank status: active, inactive")

class Bank(BankBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===============================================
# PLEDGE PAYMENT MODELS
# ===============================================

class PledgePaymentBase(BaseModel):
    pledge_id: int = Field(..., description="ID of the pledge")
    payment_date: Optional[date] = Field(None, description="Payment date (defaults to current date)")
    payment_type: str = Field(..., description="Type of payment: interest, principal, partial_redeem, full_redeem")
    amount: float = Field(..., gt=0, description="Payment amount")
    interest_amount: Optional[float] = Field(0.0, ge=0, description="Interest portion of payment")
    principal_amount: Optional[float] = Field(0.0, ge=0, description="Principal portion of payment")
    penalty_amount: Optional[float] = Field(0.0, ge=0, description="Penalty amount")
    discount_amount: Optional[float] = Field(0.0, ge=0, description="Discount amount")
    payment_method: Optional[str] = Field("cash", description="Payment method: cash, bank_transfer, cheque")
    bank_reference: Optional[str] = Field(None, max_length=100, description="Bank reference for non-cash payments")
    remarks: Optional[str] = Field(None, description="Payment remarks")

class PledgePaymentCreate(PledgePaymentBase):
    pass

class PledgePaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    payment_type: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    interest_amount: Optional[float] = Field(None, ge=0)
    principal_amount: Optional[float] = Field(None, ge=0)
    penalty_amount: Optional[float] = Field(None, ge=0)
    discount_amount: Optional[float] = Field(None, ge=0)
    payment_method: Optional[str] = None
    bank_reference: Optional[str] = Field(None, max_length=100)
    receipt_no: Optional[str] = Field(None, max_length=50)
    remarks: Optional[str] = None

class PledgePayment(PledgePaymentBase):
    payment_id: int
    receipt_no: str = Field(..., description="Auto-generated receipt number")
    balance_amount: float
    created_at: datetime
    created_by: int
    company_id: int

    class Config:
        from_attributes = True

class PledgePaymentWithDetails(PledgePayment):
    """Extended payment model with pledge and user details"""
    pledge_no: Optional[str] = None
    customer_name: Optional[str] = None
    created_by_username: Optional[str] = None


# ===============================================
# PLEDGE SETTLEMENT MODELS
# ===============================================

class InterestPeriodDetail(BaseModel):
    """Detail for each interest calculation period"""
    period: str = Field(..., description="Period description (e.g., 'Month 1', 'Month 2')")
    from_date: date = Field(..., description="Start date of the period")
    to_date: date = Field(..., description="End date of the period")
    days: int = Field(..., description="Number of days in the period")
    rate_percent: float = Field(..., description="Monthly interest rate percentage")
    principal_amount: float = Field(..., description="Principal amount for calculation")
    interest_amount: float = Field(..., description="Interest amount for this period")
    is_mandatory: bool = Field(False, description="Whether this is mandatory first month interest")
    is_partial: bool = Field(False, description="Whether this is a partial month")

class PledgeSettlementResponse(BaseModel):
    """Complete pledge settlement details response"""
    pledge_id: int = Field(..., description="Pledge ID")
    pledge_no: str = Field(..., description="Pledge number")
    customer_name: str = Field(..., description="Customer name")
    pledge_date: date = Field(..., description="Pledge creation date")
    calculation_date: date = Field(..., description="Settlement calculation date (today)")
    status: str = Field(..., description="Current pledge status")
    
    # Loan details
    loan_amount: float = Field(..., description="Original principal/loan amount")
    scheme_interest_rate: float = Field(..., description="Monthly interest rate from scheme")
    
    # Interest calculations
    total_interest: float = Field(..., description="Total accrued interest including mandatory first month")
    first_month_interest: float = Field(..., description="Mandatory first month interest (always charged)")
    accrued_interest: float = Field(..., description="Additional interest accrued over time")
    interest_calculation_details: List[InterestPeriodDetail] = Field(..., description="Breakdown of interest calculation by period")
    
    # Payment details
    paid_interest: float = Field(..., description="Total interest payments made")
    paid_principal: float = Field(..., description="Total principal payments made")
    total_paid_amount: float = Field(..., description="Total amount paid (interest + principal)")
    
    # Settlement amount
    final_amount: float = Field(..., description="Final settlement amount = loan_amount + total_interest - total_paid_amount")
    remaining_interest: float = Field(..., description="Unpaid interest amount")
    remaining_principal: float = Field(..., description="Unpaid principal amount")
    
    class Config:
        from_attributes = True


# ===============================================
# PLEDGE WITH ITEMS MODELS
# ===============================================

# Models for creating pledge items within pledge creation
class PledgeItemCreateData(BaseModel):
    jewell_design_id: int = Field(..., description="ID of the jewell design")
    jewell_condition: str = Field(..., max_length=100, description="Condition of the item")
    gross_weight: float = Field(..., ge=0, description="Gross weight of the item")
    net_weight: float = Field(..., ge=0, description="Net weight of the item")
    net_value: float = Field(..., ge=0, description="Net value of the item")
    remarks: Optional[str] = Field(None, description="Additional remarks for the item")
    # Note: image will be handled separately through file upload

# Models for updating pledge items within pledge update
class PledgeItemUpdateData(BaseModel):
    pledge_item_id: Optional[int] = Field(None, description="ID for existing items (for update/delete)")
    jewell_design_id: int = Field(..., description="ID of the jewell design")
    jewell_condition: str = Field(..., max_length=100, description="Condition of the item")
    gross_weight: float = Field(..., ge=0, description="Gross weight of the item")
    net_weight: float = Field(..., ge=0, description="Net weight of the item")
    net_value: float = Field(..., ge=0, description="Net value of the item")
    remarks: Optional[str] = Field(None, description="Additional remarks for the item")
    action: str = Field("keep", description="Action: 'keep', 'delete', 'update', 'add'")

# Comprehensive pledge creation model with items
class PledgeWithItemsCreate(BaseModel):
    # Pledge basic information
    customer_id: int = Field(..., description="ID of the customer")
    scheme_id: int = Field(..., description="ID of the scheme")
    pledge_date: date = Field(..., description="Date of pledge")
    due_date: date = Field(..., description="Due date for the pledge")
    document_charges: Optional[float] = Field(0.0, ge=0, description="Document charges")
    first_month_interest: float = Field(..., ge=0, description="First month interest amount")
    total_loan_amount: float = Field(..., ge=0, description="Total loan amount")
    final_amount: float = Field(..., ge=0, description="Final amount")
    status: Optional[str] = Field("active", description="Pledge status")
    is_move_to_bank: Optional[bool] = Field(False, description="Is moved to bank")
    remarks: Optional[str] = Field(None, description="Pledge remarks")
    
    # Pledge items
    items: List[PledgeItemCreateData] = Field(..., description="List of pledge items")
    
    # Auto-calculation flags
    auto_calculate_weights: Optional[bool] = Field(True, description="Auto-calculate gross/net weights from items")
    auto_calculate_item_count: Optional[bool] = Field(True, description="Auto-calculate item count from items")

# Comprehensive pledge update model with items
class PledgeWithItemsUpdate(BaseModel):
    # Pledge basic information (all optional for partial updates)
    customer_id: Optional[int] = Field(None, description="ID of the customer")
    scheme_id: Optional[int] = Field(None, description="ID of the scheme")
    pledge_date: Optional[date] = Field(None, description="Date of pledge")
    due_date: Optional[date] = Field(None, description="Due date for the pledge")
    document_charges: Optional[float] = Field(None, ge=0, description="Document charges")
    first_month_interest: Optional[float] = Field(None, ge=0, description="First month interest amount")
    total_loan_amount: Optional[float] = Field(None, ge=0, description="Total loan amount")
    final_amount: Optional[float] = Field(None, ge=0, description="Final amount")
    status: Optional[str] = Field(None, description="Pledge status")
    is_move_to_bank: Optional[bool] = Field(None, description="Is moved to bank")
    remarks: Optional[str] = Field(None, description="Pledge remarks")
    
    # Pledge items operations
    items: Optional[List[PledgeItemUpdateData]] = Field(None, description="List of pledge items with actions")
    
    # Items to delete (by ID)
    delete_item_ids: Optional[List[int]] = Field(default_factory=list, description="List of pledge item IDs to delete")
    
    # Auto-calculation flags
    auto_calculate_weights: Optional[bool] = Field(True, description="Auto-calculate gross/net weights from items")
    auto_calculate_item_count: Optional[bool] = Field(True, description="Auto-calculate item count from items")

# Response models
class PledgeWithItemsResponse(BaseModel):
    success: bool
    message: str
    pledge: PledgeDetailView
    items_created: Optional[int] = 0
    items_updated: Optional[int] = 0
    items_deleted: Optional[int] = 0
    warnings: Optional[List[str]] = Field(default_factory=list)


# Health check endpoint (no authentication required)
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.api_version,
        "environment": settings.environment
    }

# Company endpoints

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = authenticate_user(db, form_data.username, form_data.password)
    db.close()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", dependencies=[Depends(get_current_user)])
def read_root(current_user = Depends(get_current_user)):
    return {"message": f"Welcome to PawnProApi, {current_user.username}!"}

@app.get("/users/me", response_model=User)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

# User CRUD endpoints
@app.post("/users", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_admin_user)):
    # Check if username already exists
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if company exists
    company = db.query(CompanyModel).filter(CompanyModel.id == user.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create new user
    db_user = UserModel(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        company_id=user.company_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_admin_user)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserBase, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_admin_user)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if company exists if company_id is being updated
    if hasattr(user_update, 'company_id') and user_update.company_id is not None:
        company = db.query(CompanyModel).filter(CompanyModel.id == user_update.company_id).first()
        if not company:
            raise HTTPException(status_code=400, detail="Company not found")
    
    # Update user fields
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_admin_user)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# Company endpoints
@app.get("/companies", response_model=List[Company])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    companies = db.query(CompanyModel).offset(skip).limit(limit).all()
    return companies

@app.get("/companies/{company_id}", response_model=Company)
def read_company(company_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@app.post("/companies", response_model=Company)
def create_company(company: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_company = CompanyModel(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@app.put("/companies/{company_id}", response_model=Company)
def update_company(company_id: int, company: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    for key, value in company.dict().items():
        setattr(db_company, key, value)
    db.commit()
    db.refresh(db_company)
    return db_company

@app.delete("/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(db_company)
    db.commit()
    return {"message": "Company deleted"}

# Area endpoints
@app.get("/areas", response_model=List[Area])
def read_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    areas = db.query(AreaModel).offset(skip).limit(limit).all()
    return areas

@app.get("/areas/{area_id}", response_model=Area)
def read_area(area_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    area = db.query(AreaModel).filter(AreaModel.id == area_id).first()
    if area is None:
        raise HTTPException(status_code=404, detail="Area not found")
    return area

@app.post("/areas", response_model=Area)
def create_area(area: AreaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Validate company exists
    company = db.query(CompanyModel).filter(CompanyModel.id == area.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    db_area = AreaModel(**area.dict())
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area

@app.put("/areas/{area_id}", response_model=Area)
def update_area(area_id: int, area: AreaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_area = db.query(AreaModel).filter(AreaModel.id == area_id).first()
    if db_area is None:
        raise HTTPException(status_code=404, detail="Area not found")
    # Validate company
    company = db.query(CompanyModel).filter(CompanyModel.id == area.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    for key, value in area.dict().items():
        setattr(db_area, key, value)
    db.commit()
    db.refresh(db_area)
    return db_area

@app.delete("/areas/{area_id}")
def delete_area(area_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_area = db.query(AreaModel).filter(AreaModel.id == area_id).first()
    if db_area is None:
        raise HTTPException(status_code=404, detail="Area not found")
    db.delete(db_area)
    db.commit()
    return {"message": "Area deleted"}

# GoldSilverRate endpoints
@app.get("/gold_silver_rates", response_model=List[GoldSilverRate])
def read_gold_silver_rates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    gold_silver_rates = db.query(GoldSilverRateModel).offset(skip).limit(limit).all()
    return gold_silver_rates

@app.get("/gold_silver_rates/{rate_id}", response_model=GoldSilverRate)
def read_gold_silver_rate(rate_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    gold_silver_rate = db.query(GoldSilverRateModel).filter(GoldSilverRateModel.id == rate_id).first()
    if gold_silver_rate is None:
        raise HTTPException(status_code=404, detail="GoldSilverRate not found")
    return gold_silver_rate

@app.post("/gold_silver_rates", response_model=GoldSilverRate)
def create_gold_silver_rate(gold_silver_rate: GoldSilverRateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Validate company exists
    company = db.query(CompanyModel).filter(CompanyModel.id == gold_silver_rate.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    # Validate user exists
    user = db.query(UserModel).filter(UserModel.id == gold_silver_rate.created_by).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    db_gold_silver_rate = GoldSilverRateModel(**gold_silver_rate.dict())
    db.add(db_gold_silver_rate)
    db.commit()
    db.refresh(db_gold_silver_rate)
    return db_gold_silver_rate

@app.put("/gold_silver_rates/{rate_id}", response_model=GoldSilverRate)
def update_gold_silver_rate(rate_id: int, gold_silver_rate: GoldSilverRateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_gold_silver_rate = db.query(GoldSilverRateModel).filter(GoldSilverRateModel.id == rate_id).first()
    if db_gold_silver_rate is None:
        raise HTTPException(status_code=404, detail="GoldSilverRate not found")
    # Validate company and user
    company = db.query(CompanyModel).filter(CompanyModel.id == gold_silver_rate.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    user = db.query(UserModel).filter(UserModel.id == gold_silver_rate.created_by).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    for key, value in gold_silver_rate.dict().items():
        setattr(db_gold_silver_rate, key, value)
    db.commit()
    db.refresh(db_gold_silver_rate)
    return db_gold_silver_rate

@app.delete("/gold_silver_rates/{rate_id}")
def delete_gold_silver_rate(rate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_gold_silver_rate = db.query(GoldSilverRateModel).filter(GoldSilverRateModel.id == rate_id).first()
    if db_gold_silver_rate is None:
        raise HTTPException(status_code=404, detail="GoldSilverRate not found")
    db.delete(db_gold_silver_rate)
    db.commit()
    return {"message": "GoldSilverRate deleted"}

# JewellDesign endpoints
@app.get("/jewell_designs", response_model=List[JewellDesign])
def read_jewell_designs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    jewell_designs = db.query(JewellDesignModel).offset(skip).limit(limit).all()
    return jewell_designs

@app.get("/jewell_designs/search", response_model=List[JewellDesign])
def search_jewell_designs(
    name: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Search jewell designs by name or status.
    You can search by name, status, or both.
    """
    query = db.query(JewellDesignModel)
    
    # Build search conditions
    conditions = []
    
    if name:
        # Case-insensitive partial match for design name
        conditions.append(JewellDesignModel.design_name.ilike(f"%{name}%"))
    
    if status:
        # Exact match for status
        conditions.append(JewellDesignModel.status.ilike(f"%{status}%"))
    
    # If no search parameters provided, return error
    if not conditions:
        raise HTTPException(status_code=400, detail="Please provide at least one search parameter: name or status")
    
    # Apply OR condition if multiple search terms
    if len(conditions) == 1:
        query = query.filter(conditions[0])
    else:
        query = query.filter(or_(*conditions))
    
    # Apply pagination and execute
    jewell_designs = query.offset(skip).limit(limit).all()
    return jewell_designs

@app.get("/jewell_designs/{design_id}", response_model=JewellDesign)
def read_jewell_design(design_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    jewell_design = db.query(JewellDesignModel).filter(JewellDesignModel.id == design_id).first()
    if jewell_design is None:
        raise HTTPException(status_code=404, detail="JewellDesign not found")
    return jewell_design

@app.post("/jewell_designs", response_model=JewellDesign)
def create_jewell_design(jewell_design: JewellDesignCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_design = JewellDesignModel(**jewell_design.dict())
    db.add(db_jewell_design)
    db.commit()
    db.refresh(db_jewell_design)
    return db_jewell_design

@app.put("/jewell_designs/{design_id}", response_model=JewellDesign)
def update_jewell_design(design_id: int, jewell_design: JewellDesignCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_design = db.query(JewellDesignModel).filter(JewellDesignModel.id == design_id).first()
    if db_jewell_design is None:
        raise HTTPException(status_code=404, detail="JewellDesign not found")
    for key, value in jewell_design.dict().items():
        setattr(db_jewell_design, key, value)
    db.commit()
    db.refresh(db_jewell_design)
    return db_jewell_design

@app.delete("/jewell_designs/{design_id}")
def delete_jewell_design(design_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_design = db.query(JewellDesignModel).filter(JewellDesignModel.id == design_id).first()
    if db_jewell_design is None:
        raise HTTPException(status_code=404, detail="JewellDesign not found")
    db.delete(db_jewell_design)
    db.commit()
    return {"message": "JewellDesign deleted"}

# JewellCondition endpoints
@app.get("/jewell_conditions", response_model=List[JewellCondition])
def read_jewell_conditions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    jewell_conditions = db.query(JewellConditionModel).offset(skip).limit(limit).all()
    return jewell_conditions

@app.get("/jewell_conditions/{condition_id}", response_model=JewellCondition)
def read_jewell_condition(condition_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    jewell_condition = db.query(JewellConditionModel).filter(JewellConditionModel.id == condition_id).first()
    if jewell_condition is None:
        raise HTTPException(status_code=404, detail="JewellCondition not found")
    return jewell_condition

@app.post("/jewell_conditions", response_model=JewellCondition)
def create_jewell_condition(jewell_condition: JewellConditionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_condition = JewellConditionModel(**jewell_condition.dict())
    db.add(db_jewell_condition)
    db.commit()
    db.refresh(db_jewell_condition)
    return db_jewell_condition

@app.put("/jewell_conditions/{condition_id}", response_model=JewellCondition)
def update_jewell_condition(condition_id: int, jewell_condition: JewellConditionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_condition = db.query(JewellConditionModel).filter(JewellConditionModel.id == condition_id).first()
    if db_jewell_condition is None:
        raise HTTPException(status_code=404, detail="JewellCondition not found")
    for key, value in jewell_condition.dict().items():
        setattr(db_jewell_condition, key, value)
    db.commit()
    db.refresh(db_jewell_condition)
    return db_jewell_condition

@app.delete("/jewell_conditions/{condition_id}")
def delete_jewell_condition(condition_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_condition = db.query(JewellConditionModel).filter(JewellConditionModel.id == condition_id).first()
    if db_jewell_condition is None:
        raise HTTPException(status_code=404, detail="JewellCondition not found")
    db.delete(db_jewell_condition)
    db.commit()
    return {"message": "JewellCondition deleted"}

# JewellType endpoints
@app.get("/jewell_types", response_model=List[JewellType])
def read_jewell_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    jewell_types = db.query(JewellTypeModel).offset(skip).limit(limit).all()
    return jewell_types

@app.get("/jewell_types/{type_id}", response_model=JewellType)
def read_jewell_type(type_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    jewell_type = db.query(JewellTypeModel).filter(JewellTypeModel.id == type_id).first()
    if jewell_type is None:
        raise HTTPException(status_code=404, detail="JewellType not found")
    return jewell_type

@app.post("/jewell_types", response_model=JewellType)
def create_jewell_type(jewell_type: JewellTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_type = JewellTypeModel(**jewell_type.dict())
    db.add(db_jewell_type)
    db.commit()
    db.refresh(db_jewell_type)
    return db_jewell_type

@app.put("/jewell_types/{type_id}", response_model=JewellType)
def update_jewell_type(type_id: int, jewell_type: JewellTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_type = db.query(JewellTypeModel).filter(JewellTypeModel.id == type_id).first()
    if db_jewell_type is None:
        raise HTTPException(status_code=404, detail="JewellType not found")
    for key, value in jewell_type.dict().items():
        setattr(db_jewell_type, key, value)
    db.commit()
    db.refresh(db_jewell_type)
    return db_jewell_type

@app.delete("/jewell_types/{type_id}")
def delete_jewell_type(type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_type = db.query(JewellTypeModel).filter(JewellTypeModel.id == type_id).first()
    if db_jewell_type is None:
        raise HTTPException(status_code=404, detail="JewellType not found")
    db.delete(db_jewell_type)
    db.commit()
    return {"message": "JewellType deleted"}

# JewellRate endpoints
@app.get("/jewell_rates", response_model=List[JewellRate])
def read_jewell_rates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    jewell_rates = db.query(JewellRateModel).offset(skip).limit(limit).all()
    return jewell_rates

@app.get("/jewell_rates/{rate_id}", response_model=JewellRate)
def read_jewell_rate(rate_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    jewell_rate = db.query(JewellRateModel).filter(JewellRateModel.id == rate_id).first()
    if jewell_rate is None:
        raise HTTPException(status_code=404, detail="JewellRate not found")
    return jewell_rate

@app.get("/jewell_rates/by_type/{type_id}", response_model=List[JewellRate])
def read_jewell_rates_by_type(type_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    jewell_rates = db.query(JewellRateModel).filter(JewellRateModel.jewell_type_id == type_id).offset(skip).limit(limit).all()
    return jewell_rates

@app.post("/jewell_rates", response_model=JewellRate)
def create_jewell_rate(jewell_rate: JewellRateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_rate = JewellRateModel(**jewell_rate.dict())
    db.add(db_jewell_rate)
    db.commit()
    db.refresh(db_jewell_rate)
    return db_jewell_rate

@app.put("/jewell_rates/{rate_id}", response_model=JewellRate)
def update_jewell_rate(rate_id: int, jewell_rate: JewellRateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_rate = db.query(JewellRateModel).filter(JewellRateModel.id == rate_id).first()
    if db_jewell_rate is None:
        raise HTTPException(status_code=404, detail="JewellRate not found")
    for key, value in jewell_rate.dict().items():
        setattr(db_jewell_rate, key, value)
    db.commit()
    db.refresh(db_jewell_rate)
    return db_jewell_rate

@app.delete("/jewell_rates/{rate_id}")
def delete_jewell_rate(rate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_jewell_rate = db.query(JewellRateModel).filter(JewellRateModel.id == rate_id).first()
    if db_jewell_rate is None:
        raise HTTPException(status_code=404, detail="JewellRate not found")
    db.delete(db_jewell_rate)
    db.commit()
    return {"message": "JewellRate deleted"}

# Scheme endpoints
@app.get("/schemes", response_model=List[Scheme])
def read_schemes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    schemes = db.query(SchemeModel).offset(skip).limit(limit).all()
    return schemes

@app.get("/schemes/{scheme_id}", response_model=Scheme)
def read_scheme(scheme_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    scheme = db.query(SchemeModel).filter(SchemeModel.id == scheme_id).first()
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@app.post("/schemes", response_model=Scheme)
def create_scheme(scheme: SchemeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Validate company exists
    company = db.query(CompanyModel).filter(CompanyModel.id == scheme.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    
    # Generate account code: Sch-XXXX
    existing_codes = db.query(SchemeModel.acc_code).filter(SchemeModel.acc_code.like("Sch-%")).all()
    max_num = 0
    for code_tuple in existing_codes:
        code = code_tuple[0]
        if code and code.startswith("Sch-"):
            try:
                num = int(code.split("-")[1])
                if num > max_num:
                    max_num = num
            except:
                pass
    new_code = f"Sch-{max_num + 1:04d}"
    
    # Create the scheme with acc_code
    scheme_data = scheme.dict()
    scheme_data['acc_code'] = new_code
    db_scheme = SchemeModel(**scheme_data)
    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)
    
    # Auto account creation for schemes has been removed
    
    return db_scheme

@app.put("/schemes/{scheme_id}", response_model=Scheme)
def update_scheme(scheme_id: int, scheme: SchemeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_scheme = db.query(SchemeModel).filter(SchemeModel.id == scheme_id).first()
    if db_scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    # Validate company
    company = db.query(CompanyModel).filter(CompanyModel.id == scheme.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    
    # Store old values for account update
    old_acc_code = db_scheme.acc_code
    old_scheme_name = db_scheme.scheme_name
    
    # Update the scheme
    for key, value in scheme.dict().items():
        setattr(db_scheme, key, value)
    db.commit()
    db.refresh(db_scheme)
    
    # Update or create corresponding subaccount
    sub_account = db.query(MasterAccountModel).filter(
        MasterAccountModel.account_code == old_acc_code,
        MasterAccountModel.company_id == scheme.company_id
    ).first()
    
    # Auto account creation and update for schemes has been removed
    
    return db_scheme

@app.delete("/schemes/{scheme_id}")
def delete_scheme(scheme_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_scheme = db.query(SchemeModel).filter(SchemeModel.id == scheme_id).first()
    if db_scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found")

    db.delete(db_scheme)
    db.commit()
    return {"message": "Scheme deleted successfully"}

# Customer endpoints
@app.get("/customers", response_model=List[Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    customers = db.query(CustomerModel).offset(skip).limit(limit).all()
    return customers

@app.get("/customers/search", response_model=List[Customer])
def search_customers(
    name: Optional[str] = None, 
    phone: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_admin_user)
):
    """
    Search customers by name or phone number.
    You can search by name, phone, or both.
    """
    query = db.query(CustomerModel)
    
    # Build search conditions
    conditions = []
    
    if name:
        # Case-insensitive partial match for name
        conditions.append(CustomerModel.name.ilike(f"%{name}%"))
    
    if phone:
        # Exact or partial match for phone
        conditions.append(CustomerModel.phone.ilike(f"%{phone}%"))
    
    # If no search parameters provided, return error
    if not conditions:
        raise HTTPException(status_code=400, detail="Please provide at least one search parameter: name or phone")
    
    # Apply OR condition if multiple search terms
    if len(conditions) == 1:
        query = query.filter(conditions[0])
    else:
        query = query.filter(or_(*conditions))
    
    # Apply pagination and execute
    customers = query.offset(skip).limit(limit).all()
    return customers

@app.get("/customers/{customer_id}", response_model=Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.post("/customers", response_model=Customer)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Validate company exists
    company = db.query(CompanyModel).filter(CompanyModel.id == customer.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    
    # Validate phone number uniqueness (globally unique)
    existing_customer = db.query(CustomerModel).filter(CustomerModel.phone == customer.phone).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer with this phone number already exists")

    # Validate area if provided
    if customer.area_id:
        area = db.query(AreaModel).filter(AreaModel.id == customer.area_id).first()
        if not area:
            raise HTTPException(status_code=400, detail="Area not found")
    # Validate user
    user = db.query(UserModel).filter(UserModel.id == customer.created_by).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Generate account code: Cus-XXXX
    existing_codes = db.query(CustomerModel.acc_code).filter(CustomerModel.acc_code.like("C-%")).all()
    max_num = 0
    for code_tuple in existing_codes:
        code = code_tuple[0]
        if code and code.startswith("C-"):
            try:
                num = int(code.split("-")[1])
                if num > max_num:
                    max_num = num
            except:
                pass
    new_code = f"C-{max_num + 1:04d}"
    
    # Create the customer with acc_code
    customer_data = customer.dict()
    customer_data['acc_code'] = new_code
    db_customer = CustomerModel(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    return db_customer

@app.put("/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    # Validate company
    company = db.query(CompanyModel).filter(CompanyModel.id == customer.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    
    # Validate phone number uniqueness (exclude current customer)
    existing_customer = db.query(CustomerModel).filter(
        CustomerModel.phone == customer.phone,
        CustomerModel.id != customer_id
    ).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
    
    # Validate area if provided
    if customer.area_id:
        area = db.query(AreaModel).filter(AreaModel.id == customer.area_id).first()
        if not area:
            raise HTTPException(status_code=400, detail="Area not found")
    # Validate user
    user = db.query(UserModel).filter(UserModel.id == customer.created_by).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    for key, value in customer.dict().items():
        setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(db_customer)
    db.commit()
    return {"message": "Customer deleted successfully"}

# Item endpoints
@app.get("/items", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    items = db.query(ItemModel).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Validate customer, scheme, company
    customer = db.query(CustomerModel).filter(CustomerModel.id == item.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Customer not found")
    scheme = db.query(SchemeModel).filter(SchemeModel.id == item.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=400, detail="Scheme not found")
    company = db.query(CompanyModel).filter(CompanyModel.id == item.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    # Validate customer, scheme, company
    customer = db.query(CustomerModel).filter(CustomerModel.id == item.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Customer not found")
    scheme = db.query(SchemeModel).filter(SchemeModel.id == item.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=400, detail="Scheme not found")
    company = db.query(CompanyModel).filter(CompanyModel.id == item.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}

# File upload endpoints
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)

def validate_file_upload(file: UploadFile) -> None:
    """Validate uploaded file size and extension"""
    # Check file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
        )
    
    # Check file extension
    if file.filename:
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=400,
                detail=f"File extension not allowed. Allowed: {', '.join(settings.allowed_extensions_list)}"
            )

@app.post("/upload/company-logo/{company_id}")
async def upload_company_logo(company_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Validate file
    validate_file_upload(file)
    
    # Validate company
    company = db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Additional validation for images
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save file
    file_path = UPLOAD_DIR / f"company_{company_id}_logo_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update company logo path (store only relative filename)
    relative_path = f"company_{company_id}_logo_{file.filename}"
    setattr(company, 'logo', relative_path)
    db.commit()
    
    return {"filename": file.filename, "path": relative_path}

@app.post("/upload/customer-photo/{customer_id}")
async def upload_customer_photo(customer_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Validate file
    validate_file_upload(file)
    
    # Validate customer
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Additional validation for images
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save file
    file_path = UPLOAD_DIR / f"customer_{customer_id}_photo_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update customer photo path (store only relative filename)
    relative_path = f"customer_{customer_id}_photo_{file.filename}"
    setattr(customer, 'photo', relative_path)
    db.commit()
    
    return {"filename": file.filename, "path": relative_path}

@app.post("/upload/customer-id-proof/{customer_id}")
async def upload_customer_id_proof(customer_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Validate file
    validate_file_upload(file)
    
    # Validate customer
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Save file (ID proof can be image or PDF)
    file_path = UPLOAD_DIR / f"customer_{customer_id}_id_proof_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update customer id_proof path (store only relative filename)
    relative_path = f"customer_{customer_id}_id_proof_{file.filename}"
    setattr(customer, 'id_proof', relative_path)
    db.commit()
    
    return {"filename": file.filename, "path": relative_path}

@app.post("/upload/item-photos/{item_id}")
async def upload_item_photos(item_id: int, files: List[UploadFile] = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Validate item
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    photo_paths = []
    for file in files:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="All files must be images")
        
        # Save file
        file_path = UPLOAD_DIR / f"item_{item_id}_photo_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Store only relative filename
        photo_paths.append(f"item_{item_id}_photo_{file.filename}")
    
    # Update item photos (comma-separated relative paths)
    setattr(item, 'photos', ",".join(photo_paths))
    db.commit()
    
    return {"uploaded_files": [str(p) for p in photo_paths]}

@app.get("/files/{file_path:path}")
async def get_file(file_path: str):
    file_location = Path("uploads") / file_path
    if not file_location.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_location, filename=file_path.split("/")[-1])

# Static file serving for uploads directory
@app.get("/uploads/{file_path:path}")
async def serve_uploaded_file(file_path: str):
    file_location = Path("uploads") / file_path
    if not file_location.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_location, filename=file_path.split("/")[-1])

# MasterAccount endpoints (Chart of Accounts)
@app.get("/accounts", response_model=List[MasterAccount])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    accounts = db.query(MasterAccountModel).filter(MasterAccountModel.company_id == current_user.company_id).offset(skip).limit(limit).all()
    return accounts

@app.get("/accounts/{account_id}", response_model=MasterAccount)
def read_account(account_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    account = db.query(MasterAccountModel).filter(MasterAccountModel.account_id == account_id, MasterAccountModel.company_id == current_user.company_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.post("/accounts", response_model=MasterAccount)
def create_account(account: MasterAccountCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_admin_user)):
    # Validate company exists
    company = db.query(CompanyModel).filter(CompanyModel.id == account.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")

    # Check if account code already exists
    existing_account = db.query(MasterAccountModel).filter(MasterAccountModel.account_code == account.account_code).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Account code already exists")

    # Validate parent account if provided
    if account.parent_id:
        parent_account = db.query(MasterAccountModel).filter(MasterAccountModel.account_id == account.parent_id).first()
        if not parent_account:
            raise HTTPException(status_code=400, detail="Parent account not found")

    db_account = MasterAccountModel(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@app.put("/accounts/{account_id}", response_model=MasterAccount)
def update_account(account_id: int, account_update: MasterAccountCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_admin_user)):
    account = db.query(MasterAccountModel).filter(MasterAccountModel.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check if account code already exists (excluding current account)
    existing_account = db.query(MasterAccountModel).filter(
        MasterAccountModel.account_code == account_update.account_code,
        MasterAccountModel.account_id != account_id
    ).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Account code already exists")

    for key, value in account_update.dict().items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)
    return account

@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_admin_user)):
    account = db.query(MasterAccountModel).filter(MasterAccountModel.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    db.commit()
    return {"message": "Account deleted successfully"}

# Voucher Master endpoints
@app.get("/vouchers", response_model=List[VoucherMaster])
def read_vouchers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    vouchers = db.query(VoucherMasterModel).filter(VoucherMasterModel.company_id == current_user.company_id).offset(skip).limit(limit).all()
    return vouchers

@app.get("/vouchers/{voucher_id}", response_model=VoucherMaster)
def read_voucher(voucher_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    voucher = db.query(VoucherMasterModel).filter(VoucherMasterModel.voucher_id == voucher_id, VoucherMasterModel.company_id == current_user.company_id).first()
    if voucher is None:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return voucher

@app.post("/vouchers", response_model=VoucherMaster)
def create_voucher(voucher: VoucherMasterCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Validate company exists
    company = db.query(CompanyModel).filter(CompanyModel.id == voucher.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Company not found")

    db_voucher = VoucherMasterModel(**voucher.dict())
    db.add(db_voucher)
    db.commit()
    db.refresh(db_voucher)
    return db_voucher

# Ledger Entries endpoints
@app.get("/ledger-entries", response_model=List[LedgerEntry])
def read_ledger_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    entries = db.query(LedgerEntryModel).join(VoucherMasterModel).filter(VoucherMasterModel.company_id == current_user.company_id).offset(skip).limit(limit).all()
    return entries

@app.post("/ledger-entries", response_model=LedgerEntry)
def create_ledger_entry(entry: LedgerEntryCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Validate voucher exists
    voucher = db.query(VoucherMasterModel).filter(VoucherMasterModel.voucher_id == entry.voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=400, detail="Voucher not found")

    # Validate account exists
    account = db.query(MasterAccountModel).filter(MasterAccountModel.account_id == entry.account_id).first()
    if not account:
        raise HTTPException(status_code=400, detail="Account not found")

    db_entry = LedgerEntryModel(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


# Pledge endpoints

def generate_pledge_no(db: Session, scheme_id: int, company_id: int) -> str:
    """Generate auto-incrementing pledge number with scheme prefix"""
    scheme = db.query(SchemeModel).filter(SchemeModel.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=400, detail="Scheme not found")

    prefix = scheme.prefix or "PL"

    # Count existing pledges for this scheme and company
    count = db.query(PledgeModel).filter(
        PledgeModel.scheme_id == scheme_id,
        PledgeModel.company_id == company_id
    ).count()

    next_number = count + 1
    return f"{prefix}-{next_number:04d}"


def generate_receipt_no(db: Session, company_id) -> str:
    """Generate auto-incrementing receipt number for pledge payments"""
    # Get current year for yearly sequence
    current_year = datetime.now().year
    
    # Count existing payments for this company in current year
    year_start = datetime(current_year, 1, 1)
    year_end = datetime(current_year + 1, 1, 1)
    
    count = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.company_id == company_id,
        PledgePaymentModel.created_at >= year_start,
        PledgePaymentModel.created_at < year_end
    ).count()
    
    next_number = count + 1
    return f"RCPT-{company_id}-{current_year}-{next_number:05d}"


def generate_first_interest_receipt_no(db: Session, company_id) -> str:
    """Generate auto-incrementing first interest receipt number"""
    # Get current year for yearly sequence
    current_year = datetime.now().year
    
    # Count existing first interest payments for this company in current year
    year_start = datetime(current_year, 1, 1)
    year_end = datetime(current_year + 1, 1, 1)
    
    count = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.company_id == company_id,
        PledgePaymentModel.receipt_no.like(f"FI-{company_id}-{current_year}-%"),
        PledgePaymentModel.created_at >= year_start,
        PledgePaymentModel.created_at < year_end
    ).count()
    
    next_number = count + 1
    return f"FI-{company_id}-{current_year}-{next_number:05d}"


def create_automatic_first_interest_payment(db: Session, pledge: PledgeModel, current_user) -> Optional[PledgePaymentModel]:
    """Create automatic first interest payment when pledge is created"""
    first_interest = getattr(pledge, 'first_month_interest', 0) or 0
    if float(first_interest) <= 0:
        return None
        
    # Generate first interest receipt number
    receipt_no = generate_first_interest_receipt_no(db, current_user.company_id)
    
    # Create first interest payment
    final_amount = getattr(pledge, 'final_amount', 0) or 0
    first_payment = PledgePaymentModel(
        pledge_id=pledge.pledge_id,
        payment_date=pledge.pledge_date,
        payment_type="first_interest",
        amount=first_interest,
        interest_amount=first_interest,
        principal_amount=0.0,
        penalty_amount=0.0,
        discount_amount=0.0,
        balance_amount=float(final_amount) - float(first_interest),
        payment_method="auto",
        bank_reference=None,
        receipt_no=receipt_no,
        remarks="Automatic first month interest payment",
        created_by=current_user.id,
        company_id=current_user.company_id
    )
    
    db.add(first_payment)
    db.flush()  # Get the payment ID
    
    return first_payment


@app.post("/pledges/", response_model=Pledge)
def create_pledge(pledge: PledgeCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Generate pledge number
    pledge_no = generate_pledge_no(db, pledge.scheme_id, pledge.company_id)

    # Validate customer exists
    customer = db.query(CustomerModel).filter(CustomerModel.id == pledge.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="Customer not found")

    # Validate scheme exists
    scheme = db.query(SchemeModel).filter(SchemeModel.id == pledge.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=400, detail="Scheme not found")

    try:
        db_pledge = PledgeModel(
            **pledge.dict(),
            pledge_no=pledge_no,
            created_by=current_user.id
        )
        db.add(db_pledge)
        db.flush()  # Get pledge ID for payment creation
        
        # Create automatic first interest payment
        first_payment = create_automatic_first_interest_payment(db, db_pledge, current_user)
        
        db.commit()
        db.refresh(db_pledge)
        
        return db_pledge
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating pledge: {str(e)}")


@app.get("/pledges/", response_model=List[Pledge])
def read_pledges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    pledges = db.query(PledgeModel).filter(PledgeModel.company_id == current_user.company_id).offset(skip).limit(limit).all()
    return pledges

@app.get("/pledges/{pledge_id}", response_model=Pledge)
def read_pledge(pledge_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    if pledge is None:
        raise HTTPException(status_code=404, detail="Pledge not found")
    return pledge

@app.put("/pledges/{pledge_id}", response_model=Pledge)
def update_pledge(pledge_id: int, pledge: PledgeCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    if db_pledge is None:
        raise HTTPException(status_code=404, detail="Pledge not found")

    for key, value in pledge.dict().items():
        setattr(db_pledge, key, value)

    db.commit()
    db.refresh(db_pledge)
    return db_pledge

@app.delete("/pledges/{pledge_id}")
def delete_pledge(pledge_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    if db_pledge is None:
        raise HTTPException(status_code=404, detail="Pledge not found")

    db.delete(db_pledge)
    db.commit()
    return {"message": "Pledge deleted successfully"}


@app.get("/pledges/{pledge_id}/detail", response_model=PledgeDetailView)
def get_pledge_detail_view(pledge_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Get comprehensive pledge details including customer, scheme, pledge items, and photos
    """
    # Query pledge with all related data using eager loading
    pledge = db.query(PledgeModel).options(
        joinedload(PledgeModel.customer),
        joinedload(PledgeModel.scheme),
        joinedload(PledgeModel.user),
        joinedload(PledgeModel.pledge_items).joinedload(PledgeItemModel.jewell_design)
    ).filter(
        PledgeModel.pledge_id == pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    
    if not pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")
    
    # Convert the pledge to the detailed view using from_orm
    # This automatically handles the conversion from SQLAlchemy models to Pydantic models
    return PledgeDetailView.model_validate(pledge)


@app.put("/pledges/{pledge_id}/comprehensive-update", response_model=PledgeUpdateResponse)
def update_pledge_comprehensive(
    pledge_id: int, 
    update_data: PledgeComprehensiveUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Comprehensive pledge update endpoint that handles:
    - Customer changes (update existing or transfer to different customer)
    - Scheme changes
    - Date modifications
    - Pledge item operations (add, update, remove)
    - Financial recalculations
    All operations are performed in a single transaction for data consistency.
    """
    
    # Start transaction
    try:
        # Fetch existing pledge with all relationships
        pledge = db.query(PledgeModel).options(
            joinedload(PledgeModel.customer),
            joinedload(PledgeModel.scheme),
            joinedload(PledgeModel.user),
            joinedload(PledgeModel.pledge_items).joinedload(PledgeItemModel.jewell_design)
        ).filter(
            PledgeModel.pledge_id == pledge_id,
            PledgeModel.company_id == current_user.company_id
        ).first()
        
        if not pledge:
            raise HTTPException(status_code=404, detail="Pledge not found")
        
        warnings = []
        changes_summary = {}
        items_added = 0
        items_updated = 0
        items_removed = 0
        
        # 1. Handle customer updates
        if update_data.change_customer_id:
            # Transfer pledge to different customer entirely
            new_customer = db.query(CustomerModel).filter(
                CustomerModel.id == update_data.change_customer_id,
                CustomerModel.company_id == current_user.company_id
            ).first()
            if not new_customer:
                raise HTTPException(status_code=400, detail="New customer not found")
            
            old_customer_id = pledge.customer_id
            setattr(pledge, 'customer_id', update_data.change_customer_id)
            changes_summary["customer_changed"] = f"From customer ID {old_customer_id} to {update_data.change_customer_id}"
            
        elif update_data.customer_updates:
            # Update existing customer information
            customer = pledge.customer
            customer_changes = []
            
            if update_data.customer_updates.name and customer.name != update_data.customer_updates.name:
                setattr(customer, 'name', update_data.customer_updates.name)
                customer_changes.append(f"name: {customer.name}")
            
            if update_data.customer_updates.address and getattr(customer, 'address', None) != update_data.customer_updates.address:
                setattr(customer, 'address', update_data.customer_updates.address)
                customer_changes.append(f"address: {customer.address}")
            
            if update_data.customer_updates.city and getattr(customer, 'city', None) != update_data.customer_updates.city:
                setattr(customer, 'city', update_data.customer_updates.city)
                customer_changes.append(f"city: {customer.city}")
            
            if update_data.customer_updates.area_id and getattr(customer, 'area_id', None) != update_data.customer_updates.area_id:
                setattr(customer, 'area_id', update_data.customer_updates.area_id)
                customer_changes.append(f"area_id: {customer.area_id}")
            
            if update_data.customer_updates.phone and getattr(customer, 'phone', None) != update_data.customer_updates.phone:
                # Check if phone number is unique
                existing_customer = db.query(CustomerModel).filter(
                    CustomerModel.phone == update_data.customer_updates.phone,
                    CustomerModel.id != customer.id,
                    CustomerModel.company_id == current_user.company_id
                ).first()
                if existing_customer:
                    raise HTTPException(status_code=400, detail="Phone number already exists for another customer")
                
                setattr(customer, 'phone', update_data.customer_updates.phone)
                customer_changes.append(f"phone: {customer.phone}")
            
            if update_data.customer_updates.id_proof_type and getattr(customer, 'id_proof_type', None) != update_data.customer_updates.id_proof_type:
                setattr(customer, 'id_proof_type', update_data.customer_updates.id_proof_type)
                customer_changes.append(f"id_proof_type: {customer.id_proof_type}")
            
            if customer_changes:
                changes_summary["customer_updated"] = customer_changes
        
        # 2. Handle scheme changes
        if update_data.scheme_id and getattr(pledge, 'scheme_id', None) != update_data.scheme_id:
            new_scheme = db.query(SchemeModel).filter(
                SchemeModel.id == update_data.scheme_id,
                SchemeModel.company_id == current_user.company_id
            ).first()
            if not new_scheme:
                raise HTTPException(status_code=400, detail="New scheme not found")
            
            old_scheme_id = pledge.scheme_id
            setattr(pledge, 'scheme_id', update_data.scheme_id)
            changes_summary["scheme_changed"] = f"From scheme ID {old_scheme_id} to {update_data.scheme_id}"
            
            if update_data.recalculate_financials:
                warnings.append("Financial recalculation based on new scheme should be implemented based on business rules")
        
        # 3. Handle basic pledge field updates
        pledge_changes = []
        
        if update_data.pledge_date and getattr(pledge, 'pledge_date', None) != update_data.pledge_date:
            setattr(pledge, 'pledge_date', update_data.pledge_date)
            pledge_changes.append(f"pledge_date: {pledge.pledge_date}")
        
        if update_data.due_date and getattr(pledge, 'due_date', None) != update_data.due_date:
            setattr(pledge, 'due_date', update_data.due_date)
            pledge_changes.append(f"due_date: {pledge.due_date}")
        
        if update_data.document_charges is not None and getattr(pledge, 'document_charges', None) != update_data.document_charges:
            setattr(pledge, 'document_charges', update_data.document_charges)
            pledge_changes.append(f"document_charges: {pledge.document_charges}")
        
        if update_data.first_month_interest is not None and getattr(pledge, 'first_month_interest', None) != update_data.first_month_interest:
            setattr(pledge, 'first_month_interest', update_data.first_month_interest)
            pledge_changes.append(f"first_month_interest: {pledge.first_month_interest}")
        
        if update_data.total_loan_amount is not None and getattr(pledge, 'total_loan_amount', None) != update_data.total_loan_amount:
            setattr(pledge, 'total_loan_amount', update_data.total_loan_amount)
            pledge_changes.append(f"total_loan_amount: {pledge.total_loan_amount}")
        
        if update_data.final_amount is not None and getattr(pledge, 'final_amount', None) != update_data.final_amount:
            setattr(pledge, 'final_amount', update_data.final_amount)
            pledge_changes.append(f"final_amount: {pledge.final_amount}")
        
        if update_data.status and getattr(pledge, 'status', None) != update_data.status:
            setattr(pledge, 'status', update_data.status)
            pledge_changes.append(f"status: {pledge.status}")
        
        if update_data.is_move_to_bank is not None and getattr(pledge, 'is_move_to_bank', None) != update_data.is_move_to_bank:
            setattr(pledge, 'is_move_to_bank', update_data.is_move_to_bank)
            pledge_changes.append(f"is_move_to_bank: {pledge.is_move_to_bank}")
        
        if update_data.remarks is not None and getattr(pledge, 'remarks', None) != update_data.remarks:
            setattr(pledge, 'remarks', update_data.remarks)
            pledge_changes.append(f"remarks: {pledge.remarks}")
        
        if pledge_changes:
            changes_summary["pledge_updated"] = pledge_changes
        
        # 4. Handle pledge item operations
        if update_data.item_operations:
            for operation in update_data.item_operations:
                if operation.operation == "add":
                    # Validate required fields for add operation
                    if not operation.jewell_design_id or not operation.jewell_condition:
                        warnings.append("Skipped add operation: jewell_design_id and jewell_condition are required")
                        continue
                    
                    # Verify jewell design exists
                    design = db.query(JewellDesignModel).filter(
                        JewellDesignModel.id == operation.jewell_design_id
                    ).first()
                    if not design:
                        warnings.append(f"Skipped add operation: jewell_design_id {operation.jewell_design_id} not found")
                        continue
                    
                    new_item = PledgeItemModel(
                        pledge_id=pledge_id,
                        jewell_design_id=operation.jewell_design_id,
                        jewell_condition=operation.jewell_condition,
                        gross_weight=operation.gross_weight or 0.0,
                        net_weight=operation.net_weight or 0.0,
                        net_value=operation.net_value or 0.0,
                        remarks=operation.remarks
                    )
                    db.add(new_item)
                    items_added += 1
                
                elif operation.operation == "update":
                    if not operation.pledge_item_id:
                        warnings.append("Skipped update operation: pledge_item_id is required")
                        continue
                    
                    item = db.query(PledgeItemModel).filter(
                        PledgeItemModel.pledge_item_id == operation.pledge_item_id,
                        PledgeItemModel.pledge_id == pledge_id
                    ).first()
                    
                    if not item:
                        warnings.append(f"Skipped update operation: pledge_item_id {operation.pledge_item_id} not found")
                        continue
                    
                    # Update fields if provided
                    if operation.jewell_design_id:
                        design = db.query(JewellDesignModel).filter(
                            JewellDesignModel.id == operation.jewell_design_id
                        ).first()
                        if design:
                            setattr(item, 'jewell_design_id', operation.jewell_design_id)
                        else:
                            warnings.append(f"Invalid jewell_design_id {operation.jewell_design_id} for item {operation.pledge_item_id}")
                    
                    if operation.jewell_condition:
                        setattr(item, 'jewell_condition', operation.jewell_condition)
                    if operation.gross_weight is not None:
                        setattr(item, 'gross_weight', operation.gross_weight)
                    if operation.net_weight is not None:
                        setattr(item, 'net_weight', operation.net_weight)
                    if operation.net_value is not None:
                        setattr(item, 'net_value', operation.net_value)
                    if operation.remarks is not None:
                        setattr(item, 'remarks', operation.remarks)
                    
                    items_updated += 1
                
                elif operation.operation == "remove":
                    if not operation.pledge_item_id:
                        warnings.append("Skipped remove operation: pledge_item_id is required")
                        continue
                    
                    item = db.query(PledgeItemModel).filter(
                        PledgeItemModel.pledge_item_id == operation.pledge_item_id,
                        PledgeItemModel.pledge_id == pledge_id
                    ).first()
                    
                    if not item:
                        warnings.append(f"Skipped remove operation: pledge_item_id {operation.pledge_item_id} not found")
                        continue
                    
                    db.delete(item)
                    items_removed += 1
                
                else:
                    warnings.append(f"Unknown operation: {operation.operation}")
        
        # 5. Recalculate weights and item count if requested
        if update_data.recalculate_weights or update_data.recalculate_item_count:
            # Flush to get updated items
            db.flush()
            
            # Recalculate from current pledge items
            current_items = db.query(PledgeItemModel).filter(
                PledgeItemModel.pledge_id == pledge_id
            ).all()
            
            if update_data.recalculate_item_count:
                setattr(pledge, 'item_count', len(current_items))
                
            if update_data.recalculate_weights:
                gross_weight = sum(item.gross_weight for item in current_items)
                net_weight = sum(item.net_weight for item in current_items)
                setattr(pledge, 'gross_weight', gross_weight)
                setattr(pledge, 'net_weight', net_weight)
                changes_summary["weights_recalculated"] = f"gross: {gross_weight}, net: {net_weight}"
        
        # Commit all changes
        db.commit()
        
        # Refresh and fetch updated pledge with all relationships for response
        db.refresh(pledge)
        updated_pledge = db.query(PledgeModel).options(
            joinedload(PledgeModel.customer),
            joinedload(PledgeModel.scheme),
            joinedload(PledgeModel.user),
            joinedload(PledgeModel.pledge_items).joinedload(PledgeItemModel.jewell_design)
        ).filter(PledgeModel.pledge_id == pledge_id).first()
        
        return PledgeUpdateResponse(
            success=True,
            message="Pledge updated successfully",
            updated_pledge=PledgeDetailView.model_validate(updated_pledge),
            warnings=warnings,
            changes_summary=changes_summary,
            items_added=items_added,
            items_updated=items_updated,
            items_removed=items_removed
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating pledge: {str(e)}")


# ===============================================
# PLEDGE WITH ITEMS ENDPOINTS
# ===============================================

@app.post("/pledges/with-items", response_model=PledgeWithItemsResponse)
def create_pledge_with_items(
    pledge_data: PledgeWithItemsCreate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new pledge with pledge items in a single transaction.
    This endpoint handles both pledge creation and associated items creation.
    """
    
    # Validate that items list is not empty
    if not pledge_data.items or len(pledge_data.items) == 0:
        raise HTTPException(status_code=400, detail="At least one pledge item is required")
    
    try:
        # Validate customer exists and belongs to user's company
        customer = db.query(CustomerModel).filter(
            CustomerModel.id == pledge_data.customer_id,
            CustomerModel.company_id == current_user.company_id
        ).first()
        if not customer:
            raise HTTPException(status_code=400, detail="Customer not found")

        # Validate scheme exists
        scheme = db.query(SchemeModel).filter(SchemeModel.id == pledge_data.scheme_id).first()
        if not scheme:
            raise HTTPException(status_code=400, detail="Scheme not found")

        # Validate all jewell designs exist
        design_ids = [item.jewell_design_id for item in pledge_data.items]
        designs = db.query(JewellDesignModel).filter(JewellDesignModel.id.in_(design_ids)).all()
        found_design_ids = {design.id for design in designs}
        
        for item in pledge_data.items:
            if item.jewell_design_id not in found_design_ids:
                raise HTTPException(status_code=400, detail=f"Jewell design ID {item.jewell_design_id} not found")

        # Generate pledge number
        pledge_no = generate_pledge_no(db, pledge_data.scheme_id, getattr(current_user, 'company_id'))

        # Calculate totals from items if auto-calculation is enabled
        if pledge_data.auto_calculate_weights:
            total_gross_weight = sum(item.gross_weight for item in pledge_data.items)
            total_net_weight = sum(item.net_weight for item in pledge_data.items)
        else:
            # If not auto-calculating, use 0 as defaults (can be updated later)
            total_gross_weight = 0.0
            total_net_weight = 0.0

        if pledge_data.auto_calculate_item_count:
            item_count = len(pledge_data.items)
        else:
            item_count = 0

        # Create pledge record
        db_pledge = PledgeModel(
            customer_id=pledge_data.customer_id,
            scheme_id=pledge_data.scheme_id,
            pledge_date=pledge_data.pledge_date,
            due_date=pledge_data.due_date,
            item_count=item_count,
            gross_weight=total_gross_weight,
            net_weight=total_net_weight,
            document_charges=pledge_data.document_charges,
            first_month_interest=pledge_data.first_month_interest,
            total_loan_amount=pledge_data.total_loan_amount,
            final_amount=pledge_data.final_amount,
            status=pledge_data.status,
            is_move_to_bank=pledge_data.is_move_to_bank,
            remarks=pledge_data.remarks,
            company_id=current_user.company_id,
            pledge_no=pledge_no,
            created_by=current_user.id
        )
        
        db.add(db_pledge)
        db.flush()  # Get the pledge ID

        # Create pledge items
        items_created = 0
        for item_data in pledge_data.items:
            db_item = PledgeItemModel(
                pledge_id=db_pledge.pledge_id,
                jewell_design_id=item_data.jewell_design_id,
                jewell_condition=item_data.jewell_condition,
                gross_weight=item_data.gross_weight,
                net_weight=item_data.net_weight,
                net_value=item_data.net_value,
                remarks=item_data.remarks
            )
            db.add(db_item)
            items_created += 1

        # Create automatic first interest payment
        first_payment = create_automatic_first_interest_payment(db, db_pledge, current_user)

        # Commit all changes
        db.commit()
        
        # Refresh and get the complete pledge with relationships
        db.refresh(db_pledge)
        complete_pledge = db.query(PledgeModel).options(
            joinedload(PledgeModel.customer),
            joinedload(PledgeModel.scheme),
            joinedload(PledgeModel.user),
            joinedload(PledgeModel.pledge_items).joinedload(PledgeItemModel.jewell_design)
        ).filter(PledgeModel.pledge_id == db_pledge.pledge_id).first()

        return PledgeWithItemsResponse(
            success=True,
            message=f"Pledge created successfully with {items_created} items",
            pledge=PledgeDetailView.model_validate(complete_pledge),
            items_created=items_created,
            items_updated=0,
            items_deleted=0
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating pledge with items: {str(e)}")


@app.put("/pledges/{pledge_id}/with-items", response_model=PledgeWithItemsResponse)
def update_pledge_with_items(
    pledge_id: int,
    update_data: PledgeWithItemsUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update an existing pledge and its items in a single transaction.
    Handles pledge updates, item additions, updates, and deletions.
    """
    
    try:
        # Fetch existing pledge with relationships
        pledge = db.query(PledgeModel).options(
            joinedload(PledgeModel.customer),
            joinedload(PledgeModel.scheme),
            joinedload(PledgeModel.user),
            joinedload(PledgeModel.pledge_items).joinedload(PledgeItemModel.jewell_design)
        ).filter(
            PledgeModel.pledge_id == pledge_id,
            PledgeModel.company_id == current_user.company_id
        ).first()
        
        if not pledge:
            raise HTTPException(status_code=404, detail="Pledge not found")

        warnings = []
        items_created = 0
        items_updated = 0
        items_deleted = 0

        # Update pledge basic information
        pledge_updates = {}
        
        if update_data.customer_id is not None:
            # Validate new customer
            customer = db.query(CustomerModel).filter(
                CustomerModel.id == update_data.customer_id,
                CustomerModel.company_id == current_user.company_id
            ).first()
            if not customer:
                raise HTTPException(status_code=400, detail="Customer not found")
            pledge_updates['customer_id'] = update_data.customer_id

        if update_data.scheme_id is not None:
            # Validate new scheme
            scheme = db.query(SchemeModel).filter(SchemeModel.id == update_data.scheme_id).first()
            if not scheme:
                raise HTTPException(status_code=400, detail="Scheme not found")
            pledge_updates['scheme_id'] = update_data.scheme_id

        # Update other pledge fields
        for field in ['pledge_date', 'due_date', 'document_charges', 'first_month_interest', 
                     'total_loan_amount', 'final_amount', 'status', 'is_move_to_bank', 'remarks']:
            value = getattr(update_data, field)
            if value is not None:
                pledge_updates[field] = value

        # Apply pledge updates
        for field, value in pledge_updates.items():
            setattr(pledge, field, value)

        # Handle item deletions first
        if update_data.delete_item_ids:
            for item_id in update_data.delete_item_ids:
                item = db.query(PledgeItemModel).filter(
                    PledgeItemModel.pledge_item_id == item_id,
                    PledgeItemModel.pledge_id == pledge_id
                ).first()
                
                if item:
                    db.delete(item)
                    items_deleted += 1
                else:
                    warnings.append(f"Pledge item ID {item_id} not found for deletion")

        # Handle item operations
        if update_data.items:
            # Validate all jewell designs exist
            design_ids = [item.jewell_design_id for item in update_data.items if item.action in ['keep', 'update', 'add']]
            if design_ids:
                designs = db.query(JewellDesignModel).filter(JewellDesignModel.id.in_(design_ids)).all()
                found_design_ids = {design.id for design in designs}
                
                for item in update_data.items:
                    if item.action in ['keep', 'update', 'add'] and item.jewell_design_id not in found_design_ids:
                        raise HTTPException(status_code=400, detail=f"Jewell design ID {item.jewell_design_id} not found")

            for item_data in update_data.items:
                if item_data.action == "add":
                    # Add new item
                    new_item = PledgeItemModel(
                        pledge_id=pledge_id,
                        jewell_design_id=item_data.jewell_design_id,
                        jewell_condition=item_data.jewell_condition,
                        gross_weight=item_data.gross_weight,
                        net_weight=item_data.net_weight,
                        net_value=item_data.net_value,
                        remarks=item_data.remarks
                    )
                    db.add(new_item)
                    items_created += 1

                elif item_data.action == "update":
                    # Update existing item
                    if not item_data.pledge_item_id:
                        warnings.append("Update action requires pledge_item_id")
                        continue
                    
                    existing_item = db.query(PledgeItemModel).filter(
                        PledgeItemModel.pledge_item_id == item_data.pledge_item_id,
                        PledgeItemModel.pledge_id == pledge_id
                    ).first()
                    
                    if existing_item:
                        setattr(existing_item, 'jewell_design_id', item_data.jewell_design_id)
                        setattr(existing_item, 'jewell_condition', item_data.jewell_condition)
                        setattr(existing_item, 'gross_weight', item_data.gross_weight)
                        setattr(existing_item, 'net_weight', item_data.net_weight)
                        setattr(existing_item, 'net_value', item_data.net_value)
                        setattr(existing_item, 'remarks', item_data.remarks)
                        items_updated += 1
                    else:
                        warnings.append(f"Pledge item ID {item_data.pledge_item_id} not found for update")

                elif item_data.action == "delete":
                    # Delete item (alternative to delete_item_ids)
                    if not item_data.pledge_item_id:
                        warnings.append("Delete action requires pledge_item_id")
                        continue
                    
                    item_to_delete = db.query(PledgeItemModel).filter(
                        PledgeItemModel.pledge_item_id == item_data.pledge_item_id,
                        PledgeItemModel.pledge_id == pledge_id
                    ).first()
                    
                    if item_to_delete:
                        db.delete(item_to_delete)
                        items_deleted += 1
                    else:
                        warnings.append(f"Pledge item ID {item_data.pledge_item_id} not found for deletion")

        # Recalculate weights and item count if requested
        if update_data.auto_calculate_weights or update_data.auto_calculate_item_count:
            # Flush to get current state
            db.flush()
            
            current_items = db.query(PledgeItemModel).filter(
                PledgeItemModel.pledge_id == pledge_id
            ).all()

            if update_data.auto_calculate_item_count:
                setattr(pledge, 'item_count', len(current_items))

            if update_data.auto_calculate_weights:
                total_gross = sum(item.gross_weight for item in current_items)
                total_net = sum(item.net_weight for item in current_items)
                setattr(pledge, 'gross_weight', total_gross)
                setattr(pledge, 'net_weight', total_net)

        # Commit all changes
        db.commit()
        
        # Refresh and get updated pledge with relationships
        db.refresh(pledge)
        updated_pledge = db.query(PledgeModel).options(
            joinedload(PledgeModel.customer),
            joinedload(PledgeModel.scheme),
            joinedload(PledgeModel.user),
            joinedload(PledgeModel.pledge_items).joinedload(PledgeItemModel.jewell_design)
        ).filter(PledgeModel.pledge_id == pledge_id).first()

        return PledgeWithItemsResponse(
            success=True,
            message="Pledge and items updated successfully",
            pledge=PledgeDetailView.model_validate(updated_pledge),
            items_created=items_created,
            items_updated=items_updated,
            items_deleted=items_deleted,
            warnings=warnings
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating pledge with items: {str(e)}")


# Pledge Item endpoints

@app.post("/pledge-items/", response_model=PledgeItem)
def create_pledge_item(pledge_item: PledgeItemCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Validate pledge exists and belongs to user's company
    pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == pledge_item.pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    if not pledge:
        raise HTTPException(status_code=400, detail="Pledge not found")

    # Validate jewell design exists
    jewell_design = db.query(JewellDesignModel).filter(JewellDesignModel.id == pledge_item.jewell_design_id).first()
    if not jewell_design:
        raise HTTPException(status_code=400, detail="Jewell design not found")

    db_item = PledgeItemModel(**pledge_item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/pledge-items/", response_model=List[PledgeItem])
def read_pledge_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    items = db.query(PledgeItemModel).join(PledgeModel).filter(
        PledgeModel.company_id == current_user.company_id
    ).offset(skip).limit(limit).all()
    return items


@app.get("/pledges/{pledge_id}/items", response_model=List[PledgeItem])
def read_pledge_items_by_pledge(pledge_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # Validate pledge exists and belongs to user's company
    pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    if not pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")

    items = db.query(PledgeItemModel).filter(PledgeItemModel.pledge_id == pledge_id).all()
    return items


@app.get("/pledge-items/{item_id}", response_model=PledgeItem)
def read_pledge_item(item_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    item = db.query(PledgeItemModel).join(PledgeModel).filter(
        PledgeItemModel.pledge_item_id == item_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Pledge item not found")
    return item


@app.put("/pledge-items/{item_id}", response_model=PledgeItem)
def update_pledge_item(item_id: int, pledge_item: PledgeItemCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_item = db.query(PledgeItemModel).join(PledgeModel).filter(
        PledgeItemModel.pledge_item_id == item_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Pledge item not found")

    for key, value in pledge_item.dict().items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/pledge-items/{item_id}")
def delete_pledge_item(item_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_item = db.query(PledgeItemModel).join(PledgeModel).filter(
        PledgeItemModel.pledge_item_id == item_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Pledge item not found")

    db.delete(db_item)
    db.commit()
    return {"message": "Pledge item deleted successfully"}


@app.delete("/pledges/{pledge_id}/items")
def delete_all_pledge_items(pledge_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Delete all pledge items for a specific pledge ID.
    This will remove all items associated with the pledge but keep the pledge record intact.
    """
    # Validate pledge exists and belongs to user's company
    pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    if not pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")

    # Get all pledge items for this pledge
    pledge_items = db.query(PledgeItemModel).filter(
        PledgeItemModel.pledge_id == pledge_id
    ).all()
    
    if not pledge_items:
        return {"message": "No pledge items found for this pledge", "deleted_count": 0}

    # Delete all pledge items
    deleted_count = len(pledge_items)
    for item in pledge_items:
        db.delete(item)
    
    # Update pledge weights and item count to zero
    setattr(pledge, 'gross_weight', 0.0)
    setattr(pledge, 'net_weight', 0.0)
    setattr(pledge, 'item_count', 0)
    
    db.commit()
    
    return {
        "message": f"All pledge items deleted successfully for pledge ID {pledge_id}", 
        "deleted_count": deleted_count,
        "pledge_updated": "Weights and item count reset to zero"
    }


# ===============================================
# PLEDGE LISTING ENDPOINTS
# ===============================================

def calculate_remaining_principal(pledge: PledgeModel, db: Session) -> float:
    """Calculate remaining principal based on payments made"""
    total_payments_result = db.query(func.sum(PledgePaymentModel.principal_amount)).filter(
        PledgePaymentModel.pledge_id == pledge.pledge_id
    ).scalar()
    
    total_payments = float(total_payments_result) if total_payments_result is not None else 0.0
    pledge_loan_amount = float(getattr(pledge, 'total_loan_amount', 0.0))
    
    return pledge_loan_amount - total_payments

def map_pledge_to_out(pledge: PledgeModel, scheme: SchemeModel, db: Session) -> dict:
    """Map pledge model to PledgeOut schema format"""
    remaining_principal = calculate_remaining_principal(pledge, db)
    
    # Convert status to uppercase as required
    status_mapping = {
        'active': 'ACTIVE',
        'redeemed': 'CLOSED',
        'auctioned': 'DEFAULTED',
        'partial_paid': 'ACTIVE'
    }
    
    # Calculate closed_at based on status
    closed_at = None
    pledge_status = getattr(pledge, 'status', 'active')
    if pledge_status in ['redeemed', 'auctioned']:
        # Get the latest payment date for closed pledges
        latest_payment = db.query(PledgePaymentModel.created_at).filter(
            PledgePaymentModel.pledge_id == pledge.pledge_id
        ).order_by(PledgePaymentModel.created_at.desc()).first()
        closed_at = latest_payment[0] if latest_payment else None
    
    return {
        "id": getattr(pledge, 'pledge_id', 0),
        "pledge_no": getattr(pledge, 'pledge_no', ''),
        "customer_id": getattr(pledge, 'customer_id', 0),
        "scheme_id": getattr(pledge, 'scheme_id', 0),
        "principal_amount": float(getattr(pledge, 'total_loan_amount', 0.0)),
        "interest_rate": float(getattr(scheme, 'interest_rate_monthly', 0.0)) if scheme else 0.0,
        "start_date": getattr(pledge, 'pledge_date', None),
        "maturity_date": getattr(pledge, 'due_date', None),
        "remaining_principal": remaining_principal,
        "status": status_mapping.get(pledge_status, 'ACTIVE'),
        "created_at": getattr(pledge, 'created_at', None),
        "closed_at": closed_at
    }

@app.get("/customers/{customer_id}/pledges/active", response_model=List[PledgeOut])
def get_customer_active_pledges(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)  # Only staff/admin can view
):
    """
    Get all active pledges for a specific customer.
    Only returns pledges with status = ACTIVE.
    """
    # Verify customer exists and belongs to user's company
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id,
        CustomerModel.company_id == current_user.company_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Query active pledges with scheme information
    pledges_query = db.query(PledgeModel, SchemeModel).join(
        SchemeModel, PledgeModel.scheme_id == SchemeModel.id
    ).filter(
        PledgeModel.customer_id == customer_id,
        PledgeModel.company_id == current_user.company_id,
        PledgeModel.status.in_(['active', 'partial_paid'])  # Both considered ACTIVE
    )
    
    # Apply pagination
    pledges = pledges_query.offset(skip).limit(limit).all()
    
    # Map to PledgeOut format
    result = []
    for pledge, scheme in pledges:
        pledge_out = map_pledge_to_out(pledge, scheme, db)
        result.append(PledgeOut(**pledge_out))
    
    return result

@app.get("/customers/{customer_id}/pledges", response_model=List[PledgeOut])
def get_customer_all_pledges(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)  # Only staff/admin can view
):
    """
    Get all pledges for a specific customer.
    Returns pledges with all statuses: ACTIVE, CLOSED, DEFAULTED.
    """
    # Verify customer exists and belongs to user's company
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id,
        CustomerModel.company_id == current_user.company_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Query all pledges with scheme information
    pledges_query = db.query(PledgeModel, SchemeModel).join(
        SchemeModel, PledgeModel.scheme_id == SchemeModel.id
    ).filter(
        PledgeModel.customer_id == customer_id,
        PledgeModel.company_id == current_user.company_id
    ).order_by(PledgeModel.created_at.desc())
    
    # Apply pagination
    pledges = pledges_query.offset(skip).limit(limit).all()
    
    # Map to PledgeOut format
    result = []
    for pledge, scheme in pledges:
        pledge_out = map_pledge_to_out(pledge, scheme, db)
        result.append(PledgeOut(**pledge_out))
    
    return result

@app.get("/schemes/{scheme_id}/pledges/active", response_model=List[PledgeOut])
def get_scheme_active_pledges(
    scheme_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)  # Only staff/admin can view
):
    """
    Get all active pledges under a specific scheme.
    Only returns pledges with status = ACTIVE.
    """
    # Verify scheme exists and belongs to user's company
    scheme = db.query(SchemeModel).filter(
        SchemeModel.id == scheme_id,
        SchemeModel.company_id == current_user.company_id
    ).first()
    
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    # Query active pledges under this scheme
    pledges_query = db.query(PledgeModel).filter(
        PledgeModel.scheme_id == scheme_id,
        PledgeModel.company_id == current_user.company_id,
        PledgeModel.status.in_(['active', 'partial_paid'])  # Both considered ACTIVE
    ).order_by(PledgeModel.created_at.desc())
    
    # Apply pagination
    pledges = pledges_query.offset(skip).limit(limit).all()
    
    # Map to PledgeOut format
    result = []
    for pledge in pledges:
        pledge_out = map_pledge_to_out(pledge, scheme, db)
        result.append(PledgeOut(**pledge_out))
    
    return result


# ===============================================
# BANK ENDPOINTS
# ===============================================

@app.post("/banks/", response_model=Bank)
def create_bank(bank: BankCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Create a new bank record"""
    # Check if bank with same name and branch already exists for this company
    existing_bank = db.query(BankModel).filter(
        BankModel.bank_name == bank.bank_name,
        BankModel.branch_name == bank.branch_name,
        BankModel.company_id == current_user.company_id
    ).first()
    
    if existing_bank:
        raise HTTPException(status_code=400, detail="Bank with same name and branch already exists")
    
    db_bank = BankModel(**bank.dict(), company_id=current_user.company_id)
    db.add(db_bank)
    db.commit()
    db.refresh(db_bank)
    return db_bank


@app.get("/banks/", response_model=List[Bank])
def read_banks(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """Get all banks for the current user's company with optional filtering"""
    query = db.query(BankModel).filter(BankModel.company_id == current_user.company_id)
    
    # Filter by status if provided
    if status:
        query = query.filter(BankModel.status == status)
    
    # Search functionality
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                BankModel.bank_name.ilike(search_filter),
                BankModel.branch_name.ilike(search_filter),
                BankModel.account_name.ilike(search_filter)
            )
        )
    
    banks = query.offset(skip).limit(limit).all()
    return banks


@app.get("/banks/{bank_id}", response_model=Bank)
def read_bank(bank_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Get a specific bank by ID"""
    bank = db.query(BankModel).filter(
        BankModel.id == bank_id,
        BankModel.company_id == current_user.company_id
    ).first()
    
    if bank is None:
        raise HTTPException(status_code=404, detail="Bank not found")
    return bank


@app.put("/banks/{bank_id}", response_model=Bank)
def update_bank(
    bank_id: int, 
    bank_update: BankUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """Update a bank record"""
    db_bank = db.query(BankModel).filter(
        BankModel.id == bank_id,
        BankModel.company_id == current_user.company_id
    ).first()
    
    if db_bank is None:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    # Check for duplicate bank name + branch combination if being updated
    if bank_update.bank_name or bank_update.branch_name:
        new_bank_name = bank_update.bank_name or db_bank.bank_name
        new_branch_name = bank_update.branch_name or db_bank.branch_name
        
        existing_bank = db.query(BankModel).filter(
            BankModel.bank_name == new_bank_name,
            BankModel.branch_name == new_branch_name,
            BankModel.company_id == current_user.company_id,
            BankModel.id != bank_id
        ).first()
        
        if existing_bank:
            raise HTTPException(status_code=400, detail="Bank with same name and branch already exists")
    
    # Update only provided fields
    update_data = bank_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_bank, field, value)
    
    db.commit()
    db.refresh(db_bank)
    return db_bank


@app.delete("/banks/{bank_id}")
def delete_bank(bank_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Delete a bank record (soft delete by setting status to inactive)"""
    db_bank = db.query(BankModel).filter(
        BankModel.id == bank_id,
        BankModel.company_id == current_user.company_id
    ).first()
    
    if db_bank is None:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    # Soft delete - set status to inactive instead of hard delete
    setattr(db_bank, 'status', 'inactive')
    db.commit()
    
    return {"message": "Bank deactivated successfully"}


@app.post("/banks/{bank_id}/activate")
def activate_bank(bank_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Reactivate an inactive bank"""
    db_bank = db.query(BankModel).filter(
        BankModel.id == bank_id,
        BankModel.company_id == current_user.company_id
    ).first()
    
    if db_bank is None:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    setattr(db_bank, 'status', 'active')
    db.commit()
    
    return {"message": "Bank activated successfully"}


# ===============================================
# PLEDGE PAYMENT ENDPOINTS
# ===============================================

@app.post("/pledge-payments/", response_model=PledgePayment)
def create_pledge_payment(
    payment: PledgePaymentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new pledge payment"""
    
    # Verify pledge exists and belongs to user's company
    pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == payment.pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    
    if not pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")
    
    # Check if pledge is active
    if pledge.status not in ['active', 'partial_paid']:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot make payment for pledge with status: {pledge.status}"
        )
    
    # Calculate current balance (total loan amount minus all previous payments)
    total_payments_result = db.query(func.sum(PledgePaymentModel.amount)).filter(
        PledgePaymentModel.pledge_id == payment.pledge_id
    ).scalar()
    total_payments = total_payments_result if total_payments_result is not None else 0.0
    
    current_balance = float(getattr(pledge, 'final_amount', 0.0)) - total_payments
    payment_amount = float(getattr(payment, 'amount', 0.0))
    
    # Validate payment amount
    if payment_amount > current_balance:
        raise HTTPException(
            status_code=400, 
            detail=f"Payment amount ({payment_amount}) exceeds remaining balance ({current_balance})"
        )
    
    # Calculate new balance
    new_balance = current_balance - payment_amount
    
    # Generate receipt number - always auto-generate for consistency
    receipt_no = generate_receipt_no(db, current_user.company_id)
    
    # Create payment record
    db_payment = PledgePaymentModel(
        pledge_id=payment.pledge_id,
        payment_date=payment.payment_date or date.today(),
        payment_type=payment.payment_type,
        amount=payment_amount,
        interest_amount=payment.interest_amount or 0.0,
        principal_amount=payment.principal_amount or 0.0,
        penalty_amount=payment.penalty_amount or 0.0,
        discount_amount=payment.discount_amount or 0.0,
        balance_amount=new_balance,
        payment_method=payment.payment_method or "cash",
        bank_reference=payment.bank_reference,
        receipt_no=receipt_no,
        remarks=payment.remarks,
        created_by=current_user.id,
        company_id=current_user.company_id
    )
    
    try:
        db.add(db_payment)
        
        # Update pledge status based on balance after payment
        # Use small epsilon for floating point comparison to handle precision issues
        epsilon = 0.01  # Allow for small rounding differences
        
        if new_balance <= epsilon:
            # Pledge is fully paid - mark as redeemed (maps to CLOSED in API)
            old_status = pledge.status
            setattr(pledge, 'status', 'redeemed')
            # Add comment in remarks if not already specified
            if not payment.remarks:
                setattr(db_payment, 'remarks', f"Full pledge settlement - Pledge closed (Balance: {new_balance:.2f})")
            print(f"🎉 Pledge {getattr(pledge, 'pledge_no', pledge.pledge_id)} status updated: {old_status} → redeemed (Balance: {new_balance:.2f})")
        elif new_balance < float(getattr(pledge, 'final_amount', 0.0)):
            # Partial payment made - mark as partial_paid (maps to ACTIVE in API)
            old_status = pledge.status
            setattr(pledge, 'status', 'partial_paid')
            print(f"📝 Pledge {getattr(pledge, 'pledge_no', pledge.pledge_id)} status updated: {old_status} → partial_paid (Balance: {new_balance:.2f})")
        # If new_balance == pledge.final_amount, status remains 'active'
        
        db.commit()
        db.refresh(db_payment)
        
        return db_payment
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating payment: {str(e)}")


@app.get("/pledge-payments/", response_model=List[PledgePaymentWithDetails])
def get_pledge_payments(
    pledge_id: Optional[int] = None,
    payment_type: Optional[str] = None,
    payment_method: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get pledge payments with optional filtering"""
    
    # Base query with joins for additional details
    query = db.query(
        PledgePaymentModel,
        PledgeModel.pledge_no,
        CustomerModel.name.label('customer_name'),
        UserModel.username.label('created_by_username')
    ).join(
        PledgeModel, PledgePaymentModel.pledge_id == PledgeModel.pledge_id
    ).join(
        CustomerModel, PledgeModel.customer_id == CustomerModel.id
    ).join(
        UserModel, PledgePaymentModel.created_by == UserModel.id
    ).filter(
        PledgePaymentModel.company_id == current_user.company_id
    )
    
    # Apply filters
    if pledge_id:
        query = query.filter(PledgePaymentModel.pledge_id == pledge_id)
    
    if payment_type:
        query = query.filter(PledgePaymentModel.payment_type == payment_type)
    
    if payment_method:
        query = query.filter(PledgePaymentModel.payment_method == payment_method)
    
    if from_date:
        query = query.filter(PledgePaymentModel.payment_date >= from_date)
    
    if to_date:
        query = query.filter(PledgePaymentModel.payment_date <= to_date)
    
    # Execute query with pagination
    results = query.order_by(PledgePaymentModel.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to response format
    payments_with_details = []
    for payment, pledge_no, customer_name, created_by_username in results:
        payment_dict = {
            **payment.__dict__,
            "pledge_no": pledge_no,
            "customer_name": customer_name,
            "created_by_username": created_by_username
        }
        payments_with_details.append(payment_dict)
    
    return payments_with_details


@app.get("/pledge-payments/{payment_id}", response_model=PledgePaymentWithDetails)
def get_pledge_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get a specific pledge payment by ID"""
    
    result = db.query(
        PledgePaymentModel,
        PledgeModel.pledge_no,
        CustomerModel.name.label('customer_name'),
        UserModel.username.label('created_by_username')
    ).join(
        PledgeModel, PledgePaymentModel.pledge_id == PledgeModel.pledge_id
    ).join(
        CustomerModel, PledgeModel.customer_id == CustomerModel.id
    ).join(
        UserModel, PledgePaymentModel.created_by == UserModel.id
    ).filter(
        PledgePaymentModel.payment_id == payment_id,
        PledgePaymentModel.company_id == current_user.company_id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment, pledge_no, customer_name, created_by_username = result
    
    return {
        **payment.__dict__,
        "pledge_no": pledge_no,
        "customer_name": customer_name,
        "created_by_username": created_by_username
    }


@app.put("/pledge-payments/{payment_id}", response_model=PledgePayment)
def update_pledge_payment(
    payment_id: int,
    payment_update: PledgePaymentUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update a pledge payment"""
    
    # Get existing payment
    db_payment = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.payment_id == payment_id,
        PledgePaymentModel.company_id == current_user.company_id
    ).first()
    
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Get the pledge
    pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == db_payment.pledge_id
    ).first()
    
    if not pledge:
        raise HTTPException(status_code=404, detail="Associated pledge not found")
    
    old_amount = db_payment.amount
    
    # Update fields if provided
    update_data = payment_update.dict(exclude_unset=True)
    
    # If amount is being updated, recalculate balance
    if 'amount' in update_data:
        new_amount = update_data['amount']
        
        # Calculate total payments excluding this payment
        other_payments = db.query(func.sum(PledgePaymentModel.amount)).filter(
            PledgePaymentModel.pledge_id == db_payment.pledge_id,
            PledgePaymentModel.payment_id != payment_id
        ).scalar() or 0.0
        
        # Calculate new balance
        new_balance = pledge.final_amount - (other_payments + new_amount)
        
        if new_balance < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Updated amount would result in overpayment. Maximum allowed: {pledge.final_amount - other_payments}"
            )
        
        update_data['balance_amount'] = new_balance
    
    # Apply updates
    for field, value in update_data.items():
        setattr(db_payment, field, value)
    
    try:
        db.commit()
        db.refresh(db_payment)
        
        # Update pledge status if amount changed
        if 'amount' in update_data:
            total_payments_result = db.query(func.sum(PledgePaymentModel.amount)).filter(
                PledgePaymentModel.pledge_id == db_payment.pledge_id
            ).scalar()
            total_payments = total_payments_result if total_payments_result is not None else 0.0
            pledge_final_amount = float(getattr(pledge, 'final_amount', 0.0))
            
            if total_payments >= pledge_final_amount:
                setattr(pledge, 'status', 'redeemed')
            elif total_payments > 0:
                setattr(pledge, 'status', 'partial_paid')
            else:
                setattr(pledge, 'status', 'active')
            
            db.commit()
        
        return db_payment
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating payment: {str(e)}")


@app.delete("/pledge-payments/{payment_id}")
def delete_pledge_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Delete a pledge payment"""
    
    # Get the payment
    db_payment = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.payment_id == payment_id,
        PledgePaymentModel.company_id == current_user.company_id
    ).first()
    
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    pledge_id = db_payment.pledge_id
    
    try:
        # Delete the payment
        db.delete(db_payment)
        
        # Update pledge status based on remaining payments
        total_payments_result = db.query(func.sum(PledgePaymentModel.amount)).filter(
            PledgePaymentModel.pledge_id == pledge_id
        ).scalar()
        total_payments = total_payments_result if total_payments_result is not None else 0.0
        
        pledge = db.query(PledgeModel).filter(PledgeModel.pledge_id == pledge_id).first()
        
        if pledge:
            pledge_final_amount = float(getattr(pledge, 'final_amount', 0.0))
            if total_payments >= pledge_final_amount:
                setattr(pledge, 'status', 'redeemed')
            elif total_payments > 0:
                setattr(pledge, 'status', 'partial_paid')
            else:
                setattr(pledge, 'status', 'active')
        
        db.commit()
        
        return {"message": "Payment deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting payment: {str(e)}")


@app.get("/pledges/{pledge_id}/payments", response_model=List[PledgePayment])
def get_payments_by_pledge(
    pledge_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get all payments for a specific pledge"""
    
    # Verify pledge exists and belongs to user's company
    pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    
    if not pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")
    
    payments = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.pledge_id == pledge_id
    ).order_by(PledgePaymentModel.created_at.desc()).all()
    
    return payments


@app.get("/pledges/{pledge_id}/payment-summary")
def get_pledge_payment_summary(
    pledge_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get payment summary for a specific pledge"""
    
    # Verify pledge exists and belongs to user's company
    pledge = db.query(PledgeModel).filter(
        PledgeModel.pledge_id == pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    
    if not pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")
    
    # Calculate payment summary
    payment_summary = db.query(
        func.count(PledgePaymentModel.payment_id).label('total_payments'),
        func.sum(PledgePaymentModel.amount).label('total_amount_paid'),
        func.sum(PledgePaymentModel.interest_amount).label('total_interest_paid'),
        func.sum(PledgePaymentModel.principal_amount).label('total_principal_paid'),
        func.sum(PledgePaymentModel.penalty_amount).label('total_penalty_paid')
    ).filter(
        PledgePaymentModel.pledge_id == pledge_id
    ).first()
    
    total_amount_paid = float(payment_summary[1]) if payment_summary and payment_summary[1] is not None else 0.0
    final_amount = getattr(pledge, 'final_amount', 0.0)
    remaining_balance = final_amount - total_amount_paid
    
    return {
        "pledge_id": pledge_id,
        "pledge_no": getattr(pledge, 'pledge_no', ''),
        "final_amount": final_amount,
        "total_payments": int(payment_summary[0]) if payment_summary and payment_summary[0] is not None else 0,
        "total_amount_paid": total_amount_paid,
        "remaining_balance": remaining_balance,
        "total_interest_paid": float(payment_summary[2]) if payment_summary and payment_summary[2] is not None else 0.0,
        "total_principal_paid": float(payment_summary[3]) if payment_summary and payment_summary[3] is not None else 0.0,
        "total_penalty_paid": float(payment_summary[4]) if payment_summary and payment_summary[4] is not None else 0.0,
        "payment_percentage": round((total_amount_paid / final_amount) * 100, 2) if final_amount > 0 else 0.0,
        "status": getattr(pledge, 'status', 'unknown')
    }


@app.get("/api/pledges/{pledge_id}/settlement", response_model=PledgeSettlementResponse)
def get_pledge_settlement_details(
    pledge_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Calculate pledge settlement details based on pawn shop business rules.
    
    Business Rules:
    1. First month interest is collected upfront at pledge creation (already paid)
    2. If settlement is within same month (< 1 month difference):
       - Settlement amount = Loan amount only (no additional interest)
    3. For each completed month after pledge date:
       - Add monthly interest = loan_amount * interest_rate
    4. Example:
       - Pledge: 2025-09-15, Settlement: 2025-09-16 → Settlement = 90,000
       - Pledge: 2025-09-15, Settlement: 2025-10-16 → Settlement = 90,000 + 1,800
       - Pledge: 2025-09-15, Settlement: 2025-11-16 → Settlement = 90,000 + 3,600
    """
    
    # Get pledge with related data
    pledge = db.query(PledgeModel).options(
        joinedload(PledgeModel.customer),
        joinedload(PledgeModel.scheme)
    ).filter(
        PledgeModel.pledge_id == pledge_id,
        PledgeModel.company_id == current_user.company_id
    ).first()
    
    if not pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")
    
    # Get all payments for this pledge
    payments = db.query(PledgePaymentModel).filter(
        PledgePaymentModel.pledge_id == pledge_id
    ).all()
    
    # Calculate total payments
    total_paid_interest = sum(getattr(payment, 'interest_amount', 0.0) or 0.0 for payment in payments)
    total_paid_principal = sum(getattr(payment, 'principal_amount', 0.0) or 0.0 for payment in payments)
    total_paid_amount = total_paid_interest + total_paid_principal
    
    # Basic pledge information
    pledge_date = getattr(pledge, 'pledge_date')
    loan_amount = getattr(pledge, 'total_loan_amount', 0.0)
    first_month_interest = getattr(pledge, 'first_month_interest', 0.0)
    monthly_interest_rate = getattr(pledge.scheme, 'interest_rate_monthly', 0.0)
    customer_name = getattr(pledge.customer, 'name', 'Unknown')
    pledge_no = getattr(pledge, 'pledge_no', '')
    status = getattr(pledge, 'status', 'unknown')
    
    # Current date for calculation
    calculation_date = date.today()
    
    # Initialize interest calculation details
    interest_details = []
    total_calculated_interest = 0.0
    
    # Calculate months difference between pledge date and calculation date
    months_diff = (calculation_date.year - pledge_date.year) * 12 + (calculation_date.month - pledge_date.month)
    
    # Adjust for day difference - if calculation day is before pledge day, subtract 1 month
    if calculation_date.day < pledge_date.day:
        months_diff -= 1
    
    # Business Rule 1: First month interest is already collected (mandatory)
    first_month_already_paid = first_month_interest
    interest_details.append(InterestPeriodDetail(
        period="Month 1 (Already Paid at Pledge Creation)",
        from_date=pledge_date,
        to_date=pledge_date + relativedelta(months=1) - relativedelta(days=1),
        days=30,  # Standard month
        rate_percent=monthly_interest_rate,
        principal_amount=loan_amount,
        interest_amount=first_month_already_paid,
        is_mandatory=True,
        is_partial=False
    ))
    total_calculated_interest = first_month_already_paid
    
    # Business Rule 2: If settlement within same month (months_diff = 0)
    if months_diff <= 0:
        # No additional interest - settlement = loan amount only
        pending_interest = 0.0
        
    else:
        # Business Rule 3: For each completed month after first month, add monthly interest
        monthly_interest_amount = loan_amount * monthly_interest_rate / 100
        pending_interest = months_diff * monthly_interest_amount
        
        # Add interest details for each completed month
        for month_num in range(1, months_diff + 1):
            month_start = pledge_date + relativedelta(months=month_num)
            month_end = month_start + relativedelta(months=1) - relativedelta(days=1)
            
            interest_details.append(InterestPeriodDetail(
                period=f"Month {month_num + 1} (Completed)",
                from_date=month_start,
                to_date=month_end,
                days=30,  # Standard month
                rate_percent=monthly_interest_rate,
                principal_amount=loan_amount,
                interest_amount=monthly_interest_amount,
                is_mandatory=False,
                is_partial=False
            ))
        
        total_calculated_interest += pending_interest
    
    # Calculate settlement amounts based on business rules
    
    # Total interest that should be collected = first month (already paid) + pending months
    total_interest_due = total_calculated_interest
    
    # Paid interest = first month interest (collected at creation) + any additional payments
    total_paid_interest = first_month_interest + sum(getattr(payment, 'interest_amount', 0.0) or 0.0 for payment in payments)
    
    # Pending interest = additional months only (first month already paid)
    if months_diff <= 0:
        pending_interest = 0.0  # Same month settlement - no additional interest
    else:
        pending_interest = months_diff * (loan_amount * monthly_interest_rate / 100)
    
    # Settlement amount = loan amount + pending interest - principal payments made
    total_paid_principal = sum(getattr(payment, 'principal_amount', 0.0) or 0.0 for payment in payments)
    remaining_principal = max(0, loan_amount - total_paid_principal)
    
    # Final settlement amount = remaining principal + pending interest
    final_settlement_amount = remaining_principal + pending_interest
    
    return PledgeSettlementResponse(
        pledge_id=pledge_id,
        pledge_no=pledge_no,
        customer_name=customer_name,
        pledge_date=pledge_date,
        calculation_date=calculation_date,
        status=status,
        loan_amount=loan_amount,
        scheme_interest_rate=monthly_interest_rate,
        total_interest=total_interest_due,
        first_month_interest=first_month_interest,
        accrued_interest=pending_interest,  # Interest accrued after first month
        interest_calculation_details=interest_details,
        paid_interest=total_paid_interest,
        paid_principal=total_paid_principal,
        total_paid_amount=total_paid_interest + total_paid_principal,
        final_amount=final_settlement_amount,
        remaining_interest=pending_interest,  # Only pending interest (first month already paid)
        remaining_principal=remaining_principal
    )


# Include API routers
app.include_router(coa_router)
app.include_router(daybook_router)

# Startup section
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8715, reload=True)
