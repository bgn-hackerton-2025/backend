from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from datetime import datetime
import enum

Base = declarative_base()

# Enums for status fields
class ProviderStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class InventoryStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD = "sold"
    RESERVED = "reserved"

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    business_name = Column(String(255), nullable=True)
    
    # Profile information
    specializations = Column(ARRAY(String), nullable=True)  # e.g., ['Electronics', 'Gadgets']
    bio = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    
    # Performance metrics
    rating = Column(Float, default=0.0)
    total_tasks_completed = Column(Integer, default=0)
    average_completion_time_minutes = Column(Integer, nullable=True)
    
    # Status and verification
    status = Column(SQLEnum(ProviderStatus), default=ProviderStatus.PENDING_VERIFICATION)
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime, nullable=True)
    
    # Business details
    business_address = Column(Text, nullable=True)
    tax_id = Column(String(50), nullable=True)
    payment_info = Column(JSON, nullable=True)  # Store payment method details
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="provider")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    
    # Basic product information
    product_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    model_number = Column(String(100), nullable=True)
    
    # Physical attributes
    condition = Column(String(50), nullable=True)  # New, Used, Refurbished, etc.
    condition_notes = Column(Text, nullable=True)
    dimensions_estimate = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    material = Column(String(100), nullable=True)
    
    # Pricing and market info
    estimated_price_min = Column(Float, nullable=True)
    estimated_price_max = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    marketability_score = Column(Float, nullable=True)  # 1-10 rating
    
    # AI analysis data
    ai_analysis_raw = Column(JSON, nullable=True)  # Store full AI response
    key_features = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Image information
    original_filename = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)  # Path to stored image
    image_content_type = Column(String(100), nullable=True)
    
    # Status and management
    status = Column(SQLEnum(InventoryStatus), default=InventoryStatus.ACTIVE)
    quantity = Column(Integer, default=1)
    sku = Column(String(100), unique=True, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = Column(DateTime, nullable=True)
    
    # Relationships
    provider = relationship("Provider", back_populates="inventory_items")