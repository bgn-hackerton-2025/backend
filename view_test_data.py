#!/usr/bin/env python3
"""
Script to view provider test data from the database
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from database.models import Provider

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

if __name__ == "__main__":
    print("🔍 Viewing provider test data...\n")
    view_providers()