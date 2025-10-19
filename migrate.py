#!/usr/bin/env python3
"""
Database migration script for Cloud Run deployment.
This script runs Alembic migrations and can be used as a Cloud Run job or startup script.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    """Run database migrations"""
    load_dotenv()
    
    print("Starting database migration...")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    
    try:
        # Run Alembic migrations
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            if result.stdout:
                print("Migration output:")
                print(result.stdout)
        else:
            print("❌ Migration failed!")
            print("Error output:")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()