from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
import uuid

from .models import Provider, InventoryItem
from .schemas import (
    ProviderCreate, ProviderUpdate,
    InventoryItemCreate, InventoryItemUpdate
)

# Provider CRUD Operations
class ProviderCRUD:
    
    @staticmethod
    def create_provider(db: Session, provider: ProviderCreate) -> Provider:
        """Create a new provider"""
        db_provider = Provider(**provider.model_dump())
        db.add(db_provider)
        db.commit()
        db.refresh(db_provider)
        return db_provider
    
    @staticmethod
    def get_provider(db: Session, provider_id: uuid.UUID) -> Optional[Provider]:
        """Get provider by ID"""
        return db.query(Provider).filter(Provider.id == provider_id).first()
    
    @staticmethod
    def get_provider_by_email(db: Session, email: str) -> Optional[Provider]:
        """Get provider by email"""
        return db.query(Provider).filter(Provider.email == email).first()
    
    @staticmethod
    def get_providers(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        specialization: Optional[str] = None
    ) -> List[Provider]:
        """Get providers with optional filters"""
        query = db.query(Provider)
        
        if status:
            query = query.filter(Provider.status == status)
        
        if specialization:
            query = query.filter(Provider.specializations.contains([specialization]))
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_provider(
        db: Session, 
        provider_id: uuid.UUID, 
        provider_update: ProviderUpdate
    ) -> Optional[Provider]:
        """Update provider information"""
        db_provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if db_provider:
            update_data = provider_update.model_dump(exclude_unset=True)
            update_data['updated_at'] = datetime.utcnow()
            
            for key, value in update_data.items():
                setattr(db_provider, key, value)
            
            db.commit()
            db.refresh(db_provider)
        return db_provider
    
    @staticmethod
    def delete_provider(db: Session, provider_id: uuid.UUID) -> bool:
        """Delete a provider"""
        db_provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if db_provider:
            db.delete(db_provider)
            db.commit()
            return True
        return False
    
    @staticmethod
    def update_provider_rating(db: Session, provider_id: uuid.UUID, new_rating: float):
        """Update provider's average rating"""
        db_provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if db_provider:
            db_provider.rating = new_rating
            db_provider.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_provider)
        return db_provider

# Inventory CRUD Operations
class InventoryCRUD:
    
    @staticmethod
    def create_inventory_item(
        db: Session, 
        item: InventoryItemCreate, 
        provider_id: uuid.UUID,
        ai_analysis: dict = None,
        image_info: dict = None
    ) -> InventoryItem:
        """Create a new inventory item"""
        item_data = item.model_dump()
        item_data['provider_id'] = provider_id
        
        if ai_analysis:
            item_data['ai_analysis_raw'] = ai_analysis
            item_data['analyzed_at'] = datetime.utcnow()
        
        if image_info:
            item_data.update(image_info)
        
        db_item = InventoryItem(**item_data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def get_inventory_item(db: Session, item_id: uuid.UUID) -> Optional[InventoryItem]:
        """Get inventory item by ID"""
        return db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    
    @staticmethod
    def get_provider_inventory(
        db: Session, 
        provider_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[InventoryItem]:
        """Get inventory items for a specific provider"""
        query = db.query(InventoryItem).filter(InventoryItem.provider_id == provider_id)
        
        if status:
            query = query.filter(InventoryItem.status == status)
        
        if category:
            query = query.filter(InventoryItem.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_inventory_item(
        db: Session, 
        item_id: uuid.UUID, 
        item_update: InventoryItemUpdate
    ) -> Optional[InventoryItem]:
        """Update inventory item"""
        db_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if db_item:
            update_data = item_update.model_dump(exclude_unset=True)
            update_data['updated_at'] = datetime.utcnow()
            
            for key, value in update_data.items():
                setattr(db_item, key, value)
            
            db.commit()
            db.refresh(db_item)
        return db_item
    
    @staticmethod
    def delete_inventory_item(db: Session, item_id: uuid.UUID) -> bool:
        """Delete inventory item"""
        db_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if db_item:
            db.delete(db_item)
            db.commit()
            return True
        return False
    
    @staticmethod
    def search_inventory(
        db: Session,
        search_term: str,
        provider_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Search inventory items by name, description, or brand"""
        query = db.query(InventoryItem)
        
        if provider_id:
            query = query.filter(InventoryItem.provider_id == provider_id)
        
        search_filter = or_(
            InventoryItem.product_name.ilike(f"%{search_term}%"),
            InventoryItem.description.ilike(f"%{search_term}%"),
            InventoryItem.brand.ilike(f"%{search_term}%"),
            InventoryItem.category.ilike(f"%{search_term}%")
        )
        
        return query.filter(search_filter).offset(skip).limit(limit).all()