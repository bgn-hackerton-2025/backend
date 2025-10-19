#!/usr/bin/env python3
"""
Script to populate the database with test provider data
"""

import os
import sys
import uuid
from datetime import datetime, timezone

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, create_tables, check_database_connection
from database.models import Provider, ProviderStatus, InventoryItem, InventoryStatus
from database.crud import ProviderCRUD

def create_test_providers():
    """Create test providers in the database"""
    
    # Check database connection
    if not check_database_connection():
        print("❌ Database connection failed! Please check your DATABASE_URL in .env file")
        return False
    
    # Create tables if they don't exist
    create_tables()
    print("✅ Database tables created/verified")
    
    # Test provider data - Charity Shops and Local Second-Hand Stores
    providers_data = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",  # Using UUID format for prov_123
            "name": "St. Vincent de Paul Charity Shop",
            "email": "manager@svpcharity.org",
            "phone": "+1-555-0123",
            "business_name": "St. Vincent de Paul Society",
            "specializations": ["Men's Clothing", "Women's Clothing", "Children's Wear"],
            "bio": "Local charity shop supporting community programs through second-hand clothing sales. We accept donations and provide affordable clothing to families in need.",
            "experience_years": 8,
            "rating": 4.6,
            "total_tasks_completed": 1247,
            "average_completion_time_minutes": 15,
            "status": ProviderStatus.ACTIVE,
            "is_verified": True,
            "business_address": "123 Main Street, Downtown, CA 90210",
            "tax_id": "12-3456789"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",  # Using UUID format for prov_456
            "name": "Goodwill Community Store", 
            "email": "info@goodwillstore.com",
            "phone": "+1-555-0456",
            "business_name": "Goodwill Industries",
            "specializations": ["Casual Wear", "Work Clothes", "Accessories"],
            "bio": "Community-focused second-hand store providing job training and employment services. We offer quality pre-owned clothing at affordable prices.",
            "experience_years": 12,
            "rating": 4.7,
            "total_tasks_completed": 1892,
            "average_completion_time_minutes": 18,
            "status": ProviderStatus.ACTIVE,
            "is_verified": True,
            "business_address": "456 Community Blvd, Midtown, NY 10001",
            "tax_id": "45-6789012"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440003",  # Using UUID format for prov_789
            "name": "Local Thrift & Treasure",
            "email": "owner@localthrift.com",
            "phone": "+1-555-0789",
            "business_name": "Local Thrift & Treasure LLC",
            "specializations": ["Vintage Finds", "Denim", "Shoes"],
            "bio": "Family-owned thrift store specializing in vintage clothing and quality second-hand items. We curate unique pieces for budget-conscious shoppers.",
            "experience_years": 6,
            "rating": 4.5,
            "total_tasks_completed": 756,
            "average_completion_time_minutes": 22,
            "status": ProviderStatus.ACTIVE,
            "is_verified": True,
            "business_address": "789 Oak Street, Suburbia, MI 48201",
            "tax_id": "78-9012345"
        }
    ]
    
    db = SessionLocal()
    try:
        created_count = 0
        
        for provider_data in providers_data:
            # Check if provider already exists
            existing_provider = db.query(Provider).filter(
                Provider.email == provider_data["email"]
            ).first()
            
            if existing_provider:
                print(f"⚠️  Provider {provider_data['name']} already exists, skipping...")
                continue
            
            # Create new provider
            new_provider = Provider(
                id=uuid.UUID(provider_data["id"]),
                name=provider_data["name"],
                email=provider_data["email"],
                phone=provider_data["phone"],
                business_name=provider_data["business_name"],
                specializations=provider_data["specializations"],
                bio=provider_data["bio"],
                experience_years=provider_data["experience_years"],
                rating=provider_data["rating"],
                total_tasks_completed=provider_data["total_tasks_completed"],
                average_completion_time_minutes=provider_data["average_completion_time_minutes"],
                status=provider_data["status"],
                is_verified=provider_data["is_verified"],
                verification_date=datetime.now(timezone.utc),
                business_address=provider_data["business_address"],
                tax_id=provider_data["tax_id"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                last_active=datetime.now(timezone.utc)
            )
            
            db.add(new_provider)
            created_count += 1
            print(f"✅ Created provider: {provider_data['name']}")
        
        db.commit()
        
        if created_count > 0:
            print(f"\n🎉 Successfully created {created_count} test providers!")
        else:
            print(f"\n📋 All providers already exist in database.")
        
        # Verify the data
        all_providers = db.query(Provider).all()
        print(f"\n📊 Total providers in database: {len(all_providers)}")
        
        for provider in all_providers:
            print(f"   • {provider.name} ({provider.email}) - Rating: {provider.rating}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating providers: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_test_inventory_items():
    """Create test inventory items in the database"""
    
    # Check database connection
    if not check_database_connection():
        print("❌ Database connection failed! Please check your DATABASE_URL in .env file")
        return False
    
    # Create tables if they don't exist
    create_tables()
    print("✅ Database tables created/verified")
    
    # Test inventory items data - Normal Everyday Thrift Items
    inventory_items_data = [
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "provider_id": "550e8400-e29b-41d4-a716-446655440001",  # St. Vincent de Paul Charity Shop
            "product_name": "Levi's 501 Jeans",
            "description": "Classic straight-leg jeans in dark blue wash. Comfortable fit with traditional button fly.",
            "category": "Clothing",
            "subcategory": "Jeans",
            "brand": "Levi's",
            "model_number": "501",
            "condition": "Good",
            "condition_notes": "Light fading at knees, no holes or stains",
            "dimensions_estimate": "32 waist x 32 length",
            "color": "Dark Blue",
            "material": "98% Cotton, 2% Elastane",
            "estimated_price_min": 8.00,
            "estimated_price_max": 15.00,
            "currency": "USD",
            "marketability_score": 7.5,
            "key_features": ["Straight Leg", "Button Fly", "Classic Fit", "Dark Wash", "Cotton Blend"],
            "tags": ["levis", "jeans", "501", "classic", "denim"],
            "confidence_score": 0.92,
            "original_filename": "levis_501_dark_blue.jpg",
            "image_url": "/uploads/inventory/levis_501_dark_blue.jpg",
            "status": InventoryStatus.ACTIVE,
            "quantity": 1,
            "sku": "LEVI-501-001"
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440002",
            "provider_id": "550e8400-e29b-41d4-a716-446655440002",  # Goodwill Community Store
            "product_name": "H&M Basic T-Shirt",
            "description": "Simple cotton t-shirt in navy blue. Perfect for layering or casual wear.",
            "category": "Clothing",
            "subcategory": "Tops",
            "brand": "H&M",
            "model_number": "Basic Tee",
            "condition": "Like New",
            "condition_notes": "Minimal wear, no stains or holes",
            "dimensions_estimate": "Medium (38-40 inch chest)",
            "color": "Navy Blue",
            "material": "100% Cotton",
            "estimated_price_min": 3.00,
            "estimated_price_max": 6.00,
            "currency": "USD",
            "marketability_score": 6.8,
            "key_features": ["Basic Design", "Cotton Material", "Casual Fit", "Navy Color", "Versatile"],
            "tags": ["hm", "tshirt", "basic", "cotton", "casual"],
            "confidence_score": 0.95,
            "original_filename": "hm_navy_tee.jpg",
            "image_url": "/uploads/inventory/hm_navy_tee.jpg",
            "status": InventoryStatus.ACTIVE,
            "quantity": 1,
            "sku": "HM-TEE-001"
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440003",
            "provider_id": "550e8400-e29b-41d4-a716-446655440003",  # Local Thrift & Treasure
            "product_name": "Diesel Denim Jacket",
            "description": "Classic denim jacket with button closure. Vintage-style wash with authentic wear patterns.",
            "category": "Clothing",
            "subcategory": "Jackets",
            "brand": "Diesel",
            "model_number": "Classic Denim",
            "condition": "Very Good",
            "condition_notes": "Some fading on sleeves, buttons all intact",
            "dimensions_estimate": "Large (42-44 inch chest)",
            "color": "Light Blue",
            "material": "100% Cotton Denim",
            "estimated_price_min": 12.00,
            "estimated_price_max": 25.00,
            "currency": "USD",
            "marketability_score": 8.2,
            "key_features": ["Denim Jacket", "Button Closure", "Vintage Wash", "Classic Style", "Diesel Brand"],
            "tags": ["diesel", "denim", "jacket", "vintage", "classic"],
            "confidence_score": 0.88,
            "original_filename": "diesel_denim_jacket.jpg",
            "image_url": "/uploads/inventory/diesel_denim_jacket.jpg",
            "status": InventoryStatus.ACTIVE,
            "quantity": 1,
            "sku": "DIES-JACKET-001"
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440004",
            "provider_id": "550e8400-e29b-41d4-a716-446655440001",  # St. Vincent de Paul Charity Shop
            "product_name": "Gap Sweater",
            "description": "Soft knit sweater in charcoal gray. Perfect for layering or wearing alone.",
            "category": "Clothing",
            "subcategory": "Sweaters",
            "brand": "Gap",
            "model_number": "Essential Sweater",
            "condition": "Good",
            "condition_notes": "Minor pilling, no stains or holes",
            "dimensions_estimate": "Medium (38-40 inch chest)",
            "color": "Charcoal Gray",
            "material": "Cotton Blend",
            "estimated_price_min": 5.00,
            "estimated_price_max": 10.00,
            "currency": "USD",
            "marketability_score": 7.0,
            "key_features": ["Soft Knit", "Charcoal Color", "Layering Piece", "Gap Brand", "Comfortable"],
            "tags": ["gap", "sweater", "knit", "charcoal", "layering"],
            "confidence_score": 0.90,
            "original_filename": "gap_charcoal_sweater.jpg",
            "image_url": "/uploads/inventory/gap_charcoal_sweater.jpg",
            "status": InventoryStatus.ACTIVE,
            "quantity": 1,
            "sku": "GAP-SWEAT-001"
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440005",
            "provider_id": "550e8400-e29b-41d4-a716-446655440002",  # Goodwill Community Store
            "product_name": "Nike Running Shoes",
            "description": "Comfortable running shoes in white with black accents. Good for casual wear or light exercise.",
            "category": "Footwear",
            "subcategory": "Sneakers",
            "brand": "Nike",
            "model_number": "Air Max",
            "condition": "Fair",
            "condition_notes": "Soles show wear, upper in good condition",
            "dimensions_estimate": "Size 9",
            "color": "White/Black",
            "material": "Mesh, Rubber Sole",
            "estimated_price_min": 8.00,
            "estimated_price_max": 18.00,
            "currency": "USD",
            "marketability_score": 7.8,
            "key_features": ["Running Shoes", "Air Max", "White/Black", "Comfortable", "Nike Brand"],
            "tags": ["nike", "running", "sneakers", "air max", "casual"],
            "confidence_score": 0.85,
            "original_filename": "nike_air_max_white.jpg",
            "image_url": "/uploads/inventory/nike_air_max_white.jpg",
            "status": InventoryStatus.ACTIVE,
            "quantity": 1,
            "sku": "NIKE-AM-001"
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440006",
            "provider_id": "550e8400-e29b-41d4-a716-446655440003",  # Local Thrift & Treasure
            "product_name": "Unbranded Denim Skirt",
            "description": "Classic A-line denim skirt in medium wash. Versatile piece for casual or dressed-up looks.",
            "category": "Clothing",
            "subcategory": "Skirts",
            "brand": None,
            "model_number": None,
            "condition": "Good",
            "condition_notes": "Light fading, zipper works well",
            "dimensions_estimate": "Size 8 (28 inch waist)",
            "color": "Medium Blue",
            "material": "100% Cotton Denim",
            "estimated_price_min": 4.00,
            "estimated_price_max": 8.00,
            "currency": "USD",
            "marketability_score": 6.5,
            "key_features": ["A-Line Cut", "Denim Material", "Zipper Closure", "Medium Wash", "Versatile"],
            "tags": ["denim", "skirt", "a-line", "casual", "versatile"],
            "confidence_score": 0.82,
            "original_filename": "denim_skirt_medium.jpg",
            "image_url": "/uploads/inventory/denim_skirt_medium.jpg",
            "status": InventoryStatus.ACTIVE,
            "quantity": 1,
            "sku": "DENIM-SKIRT-001"
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440007",
            "provider_id": "550e8400-e29b-41d4-a716-446655440001",  # St. Vincent de Paul Charity Shop
            "product_name": "Old Navy Chinos",
            "description": "Comfortable chino pants in khaki color. Perfect for casual or business casual wear.",
            "category": "Clothing",
            "subcategory": "Pants",
            "brand": "Old Navy",
            "model_number": "Classic Chinos",
            "condition": "Very Good",
            "condition_notes": "Minimal wear, no stains or holes",
            "dimensions_estimate": "32 waist x 30 length",
            "color": "Khaki",
            "material": "Cotton Blend",
            "estimated_price_min": 6.00,
            "estimated_price_max": 12.00,
            "currency": "USD",
            "marketability_score": 7.2,
            "key_features": ["Chino Style", "Khaki Color", "Cotton Blend", "Classic Fit", "Versatile"],
            "tags": ["old navy", "chinos", "khaki", "casual", "pants"],
            "confidence_score": 0.91,
            "original_filename": "old_navy_chinos.jpg",
            "image_url": "/uploads/inventory/old_navy_chinos.jpg",
            "status": InventoryStatus.ACTIVE,
            "quantity": 1,
            "sku": "ON-CHINO-001"
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440008",
            "provider_id": "550e8400-e29b-41d4-a716-446655440002",  # Goodwill Community Store
            "product_name": "Target Brand Hoodie",
            "description": "Comfortable pullover hoodie in forest green. Soft fleece lining with drawstring hood.",
            "category": "Clothing",
            "subcategory": "Hoodies",
            "brand": "Target",
            "model_number": "Goodfellow",
            "condition": "Good",
            "condition_notes": "Light pilling inside, exterior in good condition",
            "dimensions_estimate": "Large (42-44 inch chest)",
            "color": "Forest Green",
            "material": "Cotton/Polyester Blend",
            "estimated_price_min": 4.00,
            "estimated_price_max": 9.00,
            "currency": "USD",
            "marketability_score": 6.8,
            "key_features": ["Pullover Style", "Fleece Lining", "Drawstring Hood", "Forest Green", "Comfortable"],
            "tags": ["target", "hoodie", "goodfellow", "green", "casual"],
            "confidence_score": 0.87,
            "original_filename": "target_green_hoodie.jpg",
            "image_url": "/uploads/inventory/target_green_hoodie.jpg",
            "status": InventoryStatus.ACTIVE,
            "quantity": 1,
            "sku": "TGT-HOODIE-001"
        }
    ]
    
    db = SessionLocal()
    try:
        created_count = 0
        
        for item_data in inventory_items_data:
            # Check if inventory item already exists
            existing_item = db.query(InventoryItem).filter(
                InventoryItem.sku == item_data["sku"]
            ).first()
            
            if existing_item:
                print(f"⚠️  Inventory item {item_data['product_name']} already exists, skipping...")
                continue
            
            # Create new inventory item
            new_item = InventoryItem(
                id=uuid.UUID(item_data["id"]),
                provider_id=uuid.UUID(item_data["provider_id"]),
                product_name=item_data["product_name"],
                description=item_data["description"],
                category=item_data["category"],
                subcategory=item_data["subcategory"],
                brand=item_data["brand"],
                model_number=item_data["model_number"],
                condition=item_data["condition"],
                condition_notes=item_data["condition_notes"],
                dimensions_estimate=item_data["dimensions_estimate"],
                color=item_data["color"],
                material=item_data["material"],
                estimated_price_min=item_data["estimated_price_min"],
                estimated_price_max=item_data["estimated_price_max"],
                currency=item_data["currency"],
                marketability_score=item_data["marketability_score"],
                key_features=item_data["key_features"],
                tags=item_data["tags"],
                confidence_score=item_data["confidence_score"],
                original_filename=item_data["original_filename"],
                image_url=item_data["image_url"],
                status=item_data["status"],
                quantity=item_data["quantity"],
                sku=item_data["sku"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                analyzed_at=datetime.now(timezone.utc)
            )
            
            db.add(new_item)
            created_count += 1
            print(f"✅ Created inventory item: {item_data['product_name']}")
        
        db.commit()
        
        if created_count > 0:
            print(f"\n🎉 Successfully created {created_count} test inventory items!")
        else:
            print(f"\n📋 All inventory items already exist in database.")
        
        # Verify the data
        all_items = db.query(InventoryItem).all()
        print(f"\n📊 Total inventory items in database: {len(all_items)}")
        
        for item in all_items:
            print(f"   • {item.product_name} ({item.brand}) - ${item.estimated_price_min}-${item.estimated_price_max}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating inventory items: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating test provider data...")
    success = create_test_providers()
    
    if success:
        print("\n✅ Provider test data creation completed successfully!")
        print("\n🚀 Creating test inventory data...")
        inventory_success = create_test_inventory_items()
        
        if inventory_success:
            print("\n✅ Test data creation completed successfully!")
            print("\n💡 You can now test the API endpoints:")
            print("   • GET /provider/profile")
            print("   • GET /customer/providers") 
            print("   • POST /provider/upload-inventory")
            print("   • GET /customer/inventory")
        else:
            print("\n❌ Inventory test data creation failed!")
            sys.exit(1)
    else:
        print("\n❌ Provider test data creation failed!")
        sys.exit(1)