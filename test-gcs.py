#!/usr/bin/env python3
"""
Test script for Google Cloud Storage integration
"""

import os
from google.cloud import storage
from dotenv import load_dotenv

def test_gcs_connection():
    """Test Google Cloud Storage connection and bucket access"""
    load_dotenv()
    
    bucket_name = os.getenv("GCS_BUCKET")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not bucket_name:
        print("❌ GCS_BUCKET environment variable not set")
        print("Please set GCS_BUCKET in your .env file")
        return False
    
    try:
        # Initialize GCS client with explicit project ID
        if project_id:
            client = storage.Client(project=project_id)
            print(f"🔧 Using project ID: {project_id}")
        else:
            # Try to get project from gcloud config
            import subprocess
            try:
                result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    project_id = result.stdout.strip()
                    client = storage.Client(project=project_id)
                    print(f"🔧 Using project ID from gcloud config: {project_id}")
                else:
                    print("❌ Could not determine Google Cloud project ID")
                    print("Please set GOOGLE_CLOUD_PROJECT environment variable or run 'gcloud config set project YOUR_PROJECT_ID'")
                    return False
            except FileNotFoundError:
                print("❌ gcloud CLI not found and GOOGLE_CLOUD_PROJECT not set")
                print("Please install gcloud CLI or set GOOGLE_CLOUD_PROJECT environment variable")
                return False
        
        # Test bucket access
        bucket = client.bucket(bucket_name)
        
        # Try to list some objects (this tests read permission)
        blobs = list(bucket.list_blobs(max_results=1))
        
        print(f"✅ Successfully connected to GCS bucket: {bucket_name}")
        print(f"📊 Bucket location: {bucket.location}")
        print(f"📁 Storage class: {bucket.storage_class}")
        
        # Test write permission by creating a test file
        test_blob = bucket.blob("test/connection-test.txt")
        test_blob.upload_from_string("Connection test successful")
        
        print("✅ Write permission confirmed")
        
        # Clean up test file
        test_blob.delete()
        print("✅ Delete permission confirmed")
        
        return True
        
    except Exception as e:
        print(f"❌ GCS connection failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Ensure GCS_BUCKET is set to a valid bucket name")
        print("2. Authenticate with: gcloud auth application-default login")
        print("3. Check bucket exists: gsutil ls gs://your-bucket-name")
        print("4. Verify permissions on the bucket")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Cloud Storage connection...")
    test_gcs_connection()