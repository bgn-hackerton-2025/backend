from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums
class ProviderStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class InventoryStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD = "sold"
    RESERVED = "reserved"

# Provider Schemas
class ProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, max_length=20)
    business_name: Optional[str] = Field(None, max_length=255)
    specializations: Optional[List[str]] = []
    bio: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)

class ProviderCreate(ProviderBase):
    business_address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=50)

class ProviderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    business_name: Optional[str] = Field(None, max_length=255)
    specializations: Optional[List[str]] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    business_address: Optional[str] = None
    status: Optional[ProviderStatusEnum] = None

class ProviderResponse(ProviderBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    rating: float = 0.0
    total_tasks_completed: int = 0
    average_completion_time_minutes: Optional[int] = None
    status: ProviderStatusEnum
    is_verified: bool = False
    verification_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_active: Optional[datetime] = None

# Inventory Schemas
class InventoryItemBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    model_number: Optional[str] = Field(None, max_length=100)

class InventoryItemCreate(InventoryItemBase):
    condition: Optional[str] = Field(None, max_length=50)
    condition_notes: Optional[str] = None
    dimensions_estimate: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    material: Optional[str] = Field(None, max_length=100)
    quantity: int = Field(1, ge=1)
    sku: Optional[str] = Field(None, max_length=100)

class InventoryItemUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    condition: Optional[str] = Field(None, max_length=50)
    condition_notes: Optional[str] = None
    estimated_price_min: Optional[float] = Field(None, ge=0)
    estimated_price_max: Optional[float] = Field(None, ge=0)
    marketability_score: Optional[float] = Field(None, ge=1, le=10)
    status: Optional[InventoryStatusEnum] = None
    quantity: Optional[int] = Field(None, ge=0)

class AIAnalysisResult(BaseModel):
    product_name: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    key_features: List[str] = []
    brand: Optional[str] = None
    model_number: Optional[str] = None
    condition: Optional[str] = None
    condition_notes: Optional[str] = None
    dimensions_estimate: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    estimated_price_range: Optional[Dict[str, Any]] = None
    marketability_score: Optional[float] = Field(None, ge=1, le=10)
    tags: List[str] = []
    additional_notes: Optional[str] = None

class InventoryItemResponse(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    provider_id: uuid.UUID
    condition: Optional[str] = None
    condition_notes: Optional[str] = None
    dimensions_estimate: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    estimated_price_min: Optional[float] = None
    estimated_price_max: Optional[float] = None
    currency: str = "USD"
    marketability_score: Optional[float] = None
    key_features: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    confidence_score: Optional[float] = None
    original_filename: Optional[str] = None
    image_url: Optional[str] = None
    status: InventoryStatusEnum
    quantity: int = 1
    sku: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    analyzed_at: Optional[datetime] = None

class InventoryUploadResponse(BaseModel):
    inventory_id: uuid.UUID
    filename: str
    content_type: str
    upload_timestamp: datetime
    analysis_status: str
    extracted_data: AIAnalysisResult
    provider_action: str = "inventory_upload"
    status: str = "success"

# Response schemas for API endpoints
class ProviderListResponse(BaseModel):
    message: str
    providers: List[ProviderResponse]
    total_providers: int
    available_now: int

class InventoryListResponse(BaseModel):
    message: str
    inventory_items: List[InventoryItemResponse]
    total_items: int
    active_items: int

# Search Schemas
class InventorySearchRequest(BaseModel):
    category: str = Field(..., min_length=1, max_length=100, description="Required: Product category to search for")
    subcategory: Optional[str] = Field(None, max_length=100, description="Optional: Product subcategory")
    color: Optional[str] = Field(None, max_length=50, description="Optional: Product color")
    style: Optional[str] = Field(None, max_length=100, description="Optional: Style to search in key_features")
    aesthetic: Optional[str] = Field(None, max_length=100, description="Optional: Aesthetic to search in tags")

class InventorySearchResponse(BaseModel):
    message: str
    inventory_items: List[InventoryItemResponse]
    total_matches: int
    search_criteria: InventorySearchRequest