#!/usr/bin/env python3
"""
Simple GCS connectivity test - focuses on basic connection without requiring full permissions
"""

import os
from google.cloud import storage
from dotenv import load_dotenv

def simple_gcs_test():
    """Simple test to verify GCS client can be initialized"""
    load_dotenv()
    
    bucket_name = os.getenv("GCS_BUCKET")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not bucket_name:
        print("❌ GCS_BUCKET environment variable not set")
        return False
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        return False
    
    try:
        # Initialize GCS client
        client = storage.Client(project=project_id)
        print(f"✅ GCS client initialized successfully")
        print(f"🔧 Project ID: {project_id}")
        print(f"📦 Target bucket: {bucket_name}")
        
        # Try to get bucket reference (doesn't require listing permissions)
        bucket = client.bucket(bucket_name)
        print(f"✅ Bucket reference created: {bucket.name}")
        
        # Check if bucket exists (this requires minimal permissions)
        try:
            bucket.reload()
            print(f"✅ Bucket exists and is accessible")
            print(f"📊 Bucket location: {bucket.location}")
            print(f"📁 Storage class: {bucket.storage_class}")
        except Exception as e:
            print(f"⚠️  Bucket access limited: {e}")
            print("💡 This is normal for restricted permissions - uploads may still work")
        
        return True
        
    except Exception as e:
        print(f"❌ GCS client initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing basic GCS connectivity...")
    simple_gcs_test()