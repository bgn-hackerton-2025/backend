from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime
import uuid
import random

from .models import Provider, InventoryItem, InventoryStatus
from .schemas import (
    ProviderCreate, ProviderUpdate,
    InventoryItemCreate, InventoryItemUpdate,
    InventorySearchRequest
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
    
    @staticmethod
    def weighted_search_inventory(
        db: Session,
        search_request: InventorySearchRequest,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Weighted search for inventory items based on multiple criteria"""
        query = db.query(InventoryItem).filter(InventoryItem.status == InventoryStatus.ACTIVE)
        
        # Build weighted search conditions
        conditions = []
        weights = []
        
        # Category (required) - highest weight
        if search_request.category:
            category_condition = InventoryItem.category.ilike(f"%{search_request.category}%")
            conditions.append(category_condition)
            weights.append(5)  # Highest weight for required field
        
        # Subcategory (optional) - high weight
        if search_request.subcategory:
            subcategory_condition = InventoryItem.subcategory.ilike(f"%{search_request.subcategory}%")
            conditions.append(subcategory_condition)
            weights.append(4)
        
        # Color (optional) - medium weight
        if search_request.color:
            color_condition = InventoryItem.color.ilike(f"%{search_request.color}%")
            conditions.append(color_condition)
            weights.append(3)
        
        # Style in key_features (optional) - medium weight
        if search_request.style:
            style_condition = func.array_to_string(InventoryItem.key_features, ',').ilike(f"%{search_request.style}%")
            conditions.append(style_condition)
            weights.append(3)
        
        # Aesthetic in tags (optional) - medium weight
        if search_request.aesthetic:
            aesthetic_condition = func.array_to_string(InventoryItem.tags, ',').ilike(f"%{search_request.aesthetic}%")
            conditions.append(aesthetic_condition)
            weights.append(3)
        
        # If no conditions, return empty list
        if not conditions:
            return []
        
        # Apply OR logic for matching any criteria
        search_filter = and_(*conditions)
        matching_items = query.filter(search_filter).all()
        
        # Calculate weighted scores for each item
        scored_items = []
        for item in matching_items:
            score = 0
            
            # Check each condition and add weight if matched
            if search_request.category and item.category and search_request.category.lower() in item.category.lower():
                score += weights[0] if len(weights) > 0 else 0
            
            if search_request.subcategory and item.subcategory and search_request.subcategory.lower() in item.subcategory.lower():
                score += weights[1] if len(weights) > 1 else 0
            
            if search_request.color and item.color and search_request.color.lower() in item.color.lower():
                score += weights[2] if len(weights) > 2 else 0
            
            if search_request.style and item.key_features:
                style_found = any(search_request.style.lower() in feature.lower() for feature in item.key_features)
                if style_found:
                    score += weights[3] if len(weights) > 3 else 0
            
            if search_request.aesthetic and item.tags:
                aesthetic_found = any(search_request.aesthetic.lower() in tag.lower() for tag in item.tags)
                if aesthetic_found:
                    score += weights[4] if len(weights) > 4 else 0
            
            scored_items.append((item, score))
        
        # Sort by score (descending) and return top results
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in scored_items[skip:skip+limit]]
    
    @staticmethod
    def get_random_inventory_items(db: Session, limit: int = 5) -> List[InventoryItem]:
        """Get random inventory items as fallback when search returns no results"""
        total_count = db.query(InventoryItem).filter(InventoryItem.status == InventoryStatus.ACTIVE).count()
        
        if total_count == 0:
            return []
        
        # Get random offset
        random_offset = random.randint(0, max(0, total_count - limit))
        
        return db.query(InventoryItem).filter(
            InventoryItem.status == InventoryStatus.ACTIVE
        ).offset(random_offset).limit(limit).all()