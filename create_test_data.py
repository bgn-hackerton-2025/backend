#!/usr/bin/env python3
"""
Script to populate the database with test provider data
"""

import os
import sys
import uuid
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, create_tables, check_database_connection
from database.models import Provider, ProviderStatus
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
    
    # Test provider data
    providers_data = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",  # Using UUID format for prov_123
            "name": "Tech Expert Solutions",
            "email": "contact@techexpert.com",
            "phone": "+1-555-0123",
            "business_name": "Tech Expert Solutions LLC",
            "specializations": ["Electronics", "Gadgets", "Smart Devices"],
            "bio": "Leading provider of electronics classification with over 10 years of experience in consumer technology analysis.",
            "experience_years": 10,
            "rating": 4.8,
            "total_tasks_completed": 1247,
            "average_completion_time_minutes": 25,
            "status": ProviderStatus.ACTIVE,
            "is_verified": True,
            "business_address": "123 Tech Street, San Francisco, CA 94105",
            "tax_id": "12-3456789"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",  # Using UUID format for prov_456
            "name": "Fashion & Lifestyle Analysts", 
            "email": "info@fashionlifestyle.com",
            "phone": "+1-555-0456",
            "business_name": "Fashion & Lifestyle Analysts Inc.",
            "specializations": ["Clothing", "Accessories", "Home Decor"],
            "bio": "Specialized in fashion and lifestyle product classification with expertise in brand identification and trend analysis.",
            "experience_years": 7,
            "rating": 4.6,
            "total_tasks_completed": 892,
            "average_completion_time_minutes": 35,
            "status": ProviderStatus.ACTIVE,
            "is_verified": True,
            "business_address": "456 Fashion Ave, New York, NY 10001",
            "tax_id": "45-6789012"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440003",  # Using UUID format for prov_789
            "name": "Industrial Classification Co.",
            "email": "services@industrialclass.com",
            "phone": "+1-555-0789",
            "business_name": "Industrial Classification Company",
            "specializations": ["Machinery", "Tools", "Industrial Equipment"],
            "bio": "Expert industrial equipment classification service with deep knowledge of manufacturing and heavy machinery.",
            "experience_years": 15,
            "rating": 4.9,
            "total_tasks_completed": 2156,
            "average_completion_time_minutes": 45,
            "status": ProviderStatus.ACTIVE,
            "is_verified": True,
            "business_address": "789 Industrial Blvd, Detroit, MI 48201",
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
                verification_date=datetime.utcnow(),
                business_address=provider_data["business_address"],
                tax_id=provider_data["tax_id"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_active=datetime.utcnow()
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

if __name__ == "__main__":
    print("🚀 Creating test provider data...")
    success = create_test_providers()
    
    if success:
        print("\n✅ Test data creation completed successfully!")
        print("\n💡 You can now test the API endpoints:")
        print("   • GET /provider/profile")
        print("   • GET /customer/providers") 
        print("   • POST /provider/upload-inventory")
    else:
        print("\n❌ Test data creation failed!")
        sys.exit(1)