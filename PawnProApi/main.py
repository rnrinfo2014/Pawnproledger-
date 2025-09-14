from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Generator, List
from datetime import timedelta, date, datetime
import os
import shutil
from pathlib import Path

from database import SessionLocal, get_db
from auth import authenticate_user, create_access_token, Token, get_current_user, get_current_admin_user, get_password_hash
from models import Company as CompanyModel, User as UserModel, MasterAccount as MasterAccountModel, VoucherMaster as VoucherMasterModel, LedgerEntry as LedgerEntryModel, Area as AreaModel, GoldSilverRate as GoldSilverRateModel, JewellDesign as JewellDesignModel, JewellCondition as JewellConditionModel, Scheme as SchemeModel, Customer as CustomerModel, Item as ItemModel, Pledge as PledgeModel, PledgeItem as PledgeItemModel, JewellType as JewellTypeModel, JewellRate as JewellRateModel
from config import settings

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# Add CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files for uploads with configurable directory
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Pydantic models
from pydantic import BaseModel
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
        from sqlalchemy import or_
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
        from sqlalchemy import or_
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

    db_pledge = PledgeModel(
        **pledge.dict(),
        pledge_no=pledge_no,
        created_by=current_user.id
    )
    db.add(db_pledge)
    db.commit()
    db.refresh(db_pledge)
    return db_pledge


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

# Startup section
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
