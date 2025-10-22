from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.database import Base


class JewellType(Base):
    __tablename__ = "jewell_types"
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String, nullable=False, unique=True)
    status = Column(String, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    rates = relationship("JewellRate", back_populates="jewell_type")
    schemes = relationship("Scheme", back_populates="jewell_type")


class JewellRate(Base):
    __tablename__ = "jewell_rates"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    jewell_type_id = Column(Integer, ForeignKey("jewell_types.id"), nullable=False)
    rate = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    jewell_type = relationship("JewellType", back_populates="rates")
    creator = relationship("User")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    phone_number = Column(String)
    logo = Column(String)
    license_no = Column(String)
    status = Column(String, default='active')
    financial_year_start = Column(Date)
    financial_year_end = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="company")
    master_accounts = relationship("MasterAccount", back_populates="company")
    voucher_masters = relationship("VoucherMaster", back_populates="company")
    areas = relationship("Area", back_populates="company")
    gold_silver_rates = relationship("GoldSilverRate", back_populates="company")
    schemes = relationship("Scheme", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    items = relationship("Item", back_populates="company")
    pledges = relationship("Pledge", back_populates="company")
    pledge_payments = relationship("PledgePayment", back_populates="company")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # admin, user, etc.
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="users")
    voucher_masters = relationship("VoucherMaster", back_populates="user")
    gold_silver_rates = relationship("GoldSilverRate", back_populates="user")
    customers = relationship("Customer", back_populates="user")
    pledges = relationship("Pledge", back_populates="user")
    pledge_payments = relationship("PledgePayment", back_populates="user")

class MasterAccount(Base):
    __tablename__ = "accounts_master"

    account_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_name = Column(String(255), nullable=False)
    account_code = Column(String(50), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("accounts_master.account_id", ondelete="CASCADE"))
    account_type = Column(String(20), nullable=False)  # Asset, Liability, Income, Expense, Equity
    group_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Self-referencing relationship
    parent = relationship("MasterAccount", remote_side=[account_id], backref="children")
    # Other relationships
    company = relationship("Company", back_populates="master_accounts")
    ledger_entries = relationship("LedgerEntry", back_populates="account")

class VoucherMaster(Base):
    __tablename__ = "voucher_master"

    voucher_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    voucher_type = Column(String(20), nullable=False)  # Pledge, Receipt, Payment, Journal, Auction
    voucher_date = Column(Date, nullable=False, default=func.current_date())
    narration = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="voucher_masters")
    user = relationship("User", back_populates="voucher_masters")
    ledger_entries = relationship("LedgerEntry", back_populates="voucher")

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    entry_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    voucher_id = Column(Integer, ForeignKey("voucher_master.voucher_id", ondelete="CASCADE"))
    account_id = Column(Integer, ForeignKey("accounts_master.account_id", ondelete="CASCADE"), nullable=False)
    dr_cr = Column(String(1), nullable=False)  # D or C
    amount = Column(Float, nullable=False)
    debit = Column(Float, default=0.0)  # New: separate debit amount
    credit = Column(Float, default=0.0)  # New: separate credit amount
    narration = Column(String)
    description = Column(String)  # New: detailed description
    reference_type = Column(String(20))  # New: 'pledge', 'payment', etc.
    reference_id = Column(Integer)  # New: ID of the related record
    transaction_date = Column(Date, nullable=False, default=func.current_date())  # New: business date
    entry_date = Column(Date, nullable=False, default=func.current_date())
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)  # New: company reference
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    voucher = relationship("VoucherMaster", back_populates="ledger_entries")
    account = relationship("MasterAccount", back_populates="ledger_entries")
    company = relationship("Company")  # New: company relationship

class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships - assuming areas belong to companies
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="areas")
    customers = relationship("Customer", back_populates="area")

class GoldSilverRate(Base):
    __tablename__ = "gold_silver_rates"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    gold_rate_per_gram = Column(Float, nullable=False)
    silver_rate_per_gram = Column(Float, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="gold_silver_rates")
    user = relationship("User", back_populates="gold_silver_rates")

class JewellDesign(Base):
    __tablename__ = "jewell_designs"

    id = Column(Integer, primary_key=True, index=True)
    design_name = Column(String, nullable=False)
    status = Column(String, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pledge_items = relationship("PledgeItem", back_populates="jewell_design")

class JewellCondition(Base):
    __tablename__ = "jewell_conditions"

    id = Column(Integer, primary_key=True, index=True)
    condition = Column(String, nullable=False)
    status = Column(String, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    jewell_category = Column(String, nullable=False)  # gold/silver - kept for backward compatibility
    jewell_type_id = Column(Integer, ForeignKey("jewell_types.id"), nullable=True)  # New foreign key to JewellType
    scheme_name = Column(String, nullable=False)
    prefix = Column(String)
    interest_rate_monthly = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)  # in months?
    loan_allowed_percent = Column(Float, nullable=False)
    slippage_percent = Column(Float, nullable=False)
    status = Column(String, default='active')
    acc_code = Column(String)  # Auto-generated account code
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="schemes")
    jewell_type = relationship("JewellType", back_populates="schemes")
    items = relationship("Item", back_populates="scheme")
    pledges = relationship("Pledge", back_populates="scheme")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Customer_Name
    address = Column(String)
    city = Column(String)
    area_id = Column(Integer, ForeignKey("areas.id"))
    phone = Column(String, unique=True, nullable=False)  # Phone Number (unique)
    acc_code = Column(String)  # Auto-generated account code
    coa_account_id = Column(Integer, ForeignKey("accounts_master.account_id"))  # COA Account Reference
    id_proof_type = Column(String)  # Aadhaar Card, voter Id, Pancard, etc.
    id_image = Column(String)  # URL/path to ID image
    status = Column(String, default='active')
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company", back_populates="customers")
    area = relationship("Area", back_populates="customers")
    user = relationship("User", back_populates="customers")
    coa_account = relationship("MasterAccount", foreign_keys=[coa_account_id])  # COA Account relationship
    items = relationship("Item", back_populates="customer")
    pledges = relationship("Pledge", back_populates="customer")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    weight = Column(Float)  # in grams
    estimated_value = Column(Float)
    photos = Column(String)  # Comma-separated paths to photo files
    customer_id = Column(Integer, ForeignKey("customers.id"))
    scheme_id = Column(Integer, ForeignKey("schemes.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    status = Column(String, default='pawned')  # pawned, redeemed, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="items")
    scheme = relationship("Scheme", back_populates="items")
    company = relationship("Company", back_populates="items")


class Pledge(Base):
    __tablename__ = "pledges"

    pledge_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    pledge_no = Column(String(50), unique=True, nullable=False)  # Auto-generated with scheme prefix
    pledge_date = Column(Date, nullable=False, default=func.current_date())
    due_date = Column(Date, nullable=False)
    item_count = Column(Integer, nullable=False)
    gross_weight = Column(Float, nullable=False)
    net_weight = Column(Float, nullable=False)
    document_charges = Column(Float, default=0.0)
    first_month_interest = Column(Float, nullable=False)
    total_loan_amount = Column(Float, nullable=False)
    final_amount = Column(Float, nullable=False)
    status = Column(String(20), default='active')  # active, redeemed, auctioned, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_move_to_bank = Column(Boolean, default=False)
    remarks = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="pledges")
    scheme = relationship("Scheme", back_populates="pledges")
    user = relationship("User", back_populates="pledges")
    company = relationship("Company", back_populates="pledges")
    pledge_items = relationship("PledgeItem", back_populates="pledge", cascade="all, delete-orphan")
    pledge_payments = relationship("PledgePayment", back_populates="pledge", cascade="all, delete-orphan")


class PledgeItem(Base):
    __tablename__ = "pledge_items"

    pledge_item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pledge_id = Column(Integer, ForeignKey("pledges.pledge_id", ondelete="CASCADE"), nullable=False)
    jewell_design_id = Column(Integer, ForeignKey("jewell_designs.id"), nullable=False)
    jewell_condition = Column(String(100), nullable=False)
    gross_weight = Column(Float, nullable=False)
    net_weight = Column(Float, nullable=False)
    image = Column(String)  # Path to image file
    net_value = Column(Float, nullable=False)
    remarks = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pledge = relationship("Pledge", back_populates="pledge_items")
    jewell_design = relationship("JewellDesign", back_populates="pledge_items")


class Bank(Base):
    __tablename__ = "banks"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String(200), nullable=False)
    branch_name = Column(String(200))
    account_name = Column(String(200))  # Renamed from account_holder_name and simplified
    status = Column(String(20), default='active')  # active, inactive
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company")


class PledgePayment(Base):
    __tablename__ = "pledge_payments"

    payment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pledge_id = Column(Integer, ForeignKey("pledges.pledge_id", ondelete="CASCADE"), nullable=False)
    payment_date = Column(Date, nullable=False, default=func.current_date())
    payment_type = Column(String(20), nullable=False)  # interest, principal, partial_redeem, full_redeem
    amount = Column(Float, nullable=False)
    interest_amount = Column(Float, default=0.0)
    principal_amount = Column(Float, default=0.0)
    penalty_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)  # Discount applied to payment
    balance_amount = Column(Float, nullable=False)  # Remaining balance after this payment
    payment_method = Column(String(20), default='cash')  # cash, bank_transfer, cheque, etc.
    bank_reference = Column(String(100))  # For non-cash payments
    receipt_no = Column(String(50))
    remarks = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Relationships
    pledge = relationship("Pledge", back_populates="pledge_payments")
    user = relationship("User")
    company = relationship("Company")
