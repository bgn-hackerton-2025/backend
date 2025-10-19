#!/usr/bin/env python3
"""
Script to view provider and inventory test data from the database
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from database.models import Provider, InventoryItem

def view_providers():
    """Display all providers from the database"""
    
    db = SessionLocal()
    try:
        providers = db.query(Provider).all()
        
        if not providers:
            print("❌ No providers found in database")
            return
        
        print(f"📋 Found {len(providers)} providers in database:\n")
        
        for i, provider in enumerate(providers, 1):
            print(f"🏢 Provider #{i}")
            print(f"   ID: {provider.id}")
            print(f"   Name: {provider.name}")
            print(f"   Email: {provider.email}")
            print(f"   Business: {provider.business_name}")
            print(f"   Specializations: {', '.join(provider.specializations) if provider.specializations else 'None'}")
            print(f"   Rating: {provider.rating}/5.0")
            print(f"   Tasks Completed: {provider.total_tasks_completed}")
            print(f"   Avg Time: {provider.average_completion_time_minutes} minutes")
            print(f"   Status: {provider.status.value}")
            print(f"   Verified: {'✅' if provider.is_verified else '❌'}")
            print(f"   Created: {provider.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error querying providers: {e}")
    finally:
        db.close()

def view_inventory():
    """Display all inventory items from the database"""
    
    db = SessionLocal()
    try:
        inventory_items = db.query(InventoryItem).all()
        
        if not inventory_items:
            print("❌ No inventory items found in database")
            return
        
        print(f"📦 Found {len(inventory_items)} inventory items in database:\n")
        
        for i, item in enumerate(inventory_items, 1):
            print(f"📦 Inventory Item #{i}")
            print(f"   ID: {item.id}")
            print(f"   Product Name: {item.product_name}")
            print(f"   Description: {item.description or 'No description'}")
            print(f"   Category: {item.category or 'No category'}")
            print(f"   Subcategory: {item.subcategory or 'No subcategory'}")
            print(f"   Brand: {item.brand or 'No brand'}")
            print(f"   Model: {item.model_number or 'No model'}")
            print(f"   Condition: {item.condition or 'No condition specified'}")
            print(f"   Color: {item.color or 'No color specified'}")
            print(f"   Material: {item.material or 'No material specified'}")
            
            # Price information
            if item.estimated_price_min and item.estimated_price_max:
                print(f"   Price Range: {item.estimated_price_min} - {item.estimated_price_max} {item.currency}")
            elif item.estimated_price_min:
                print(f"   Price: {item.estimated_price_min} {item.currency}")
            else:
                print(f"   Price: Not specified")
            
            print(f"   Marketability Score: {item.marketability_score or 'Not rated'}")
            print(f"   Quantity: {item.quantity}")
            print(f"   Status: {item.status.value if item.status else 'No status'}")
            print(f"   Provider ID: {item.provider_id}")
            
            # Key features and tags
            if item.key_features:
                print(f"   Key Features: {', '.join(item.key_features)}")
            if item.tags:
                print(f"   Tags: {', '.join(item.tags)}")
            
            print(f"   Created: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if item.analyzed_at:
                print(f"   Analyzed: {item.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error querying inventory items: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔍 Viewing test data from database...\n")
    
    print("=" * 60)
    print("PROVIDERS")
    print("=" * 60)
    view_providers()
    
    print("\n" + "=" * 60)
    print("INVENTORY ITEMS")
    print("=" * 60)
    view_inventory()