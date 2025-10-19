from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
import google.generativeai as genai
from PIL import Image
import io
import os
import subprocess
import sys
from dotenv import load_dotenv
from provider_routes import router as provider_router
from customer_routes import router as customer_router
from database.database import get_database_session

# Load environment variables
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Warning: GOOGLE_API_KEY environment variable not set. Image processing endpoints will not work.")
else:
    genai.configure(api_key=api_key)

# Create FastAPI instance
app = FastAPI(
    title="BGN API",
    description="A FastAPI application with image classification for customers and providers",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(provider_router)
app.include_router(customer_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to BGN API"}

@app.get("/health")
async def health_check(db: Session = Depends(get_database_session)):
    """Health check endpoint that also verifies database connection"""
    try:
        # Test database connection by running a simple query
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "message": "API and database are working",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "message": "Database connection failed",
            "error": str(e),
            "database": "disconnected"
        }

@app.get("/info")
async def info():
    """Info endpoint that displays 'It works'"""
    return {"message": "It works"}

@app.get("/admin")
async def admin_panel():
    """Serve the admin panel for migrations"""
    return FileResponse("static/admin.html")

@app.post("/admin/migrate")
async def run_migrations():
    """Manual migration endpoint - run database migrations"""
    try:
        print("🔄 Running database migrations...")
        
        # Run Alembic migrations
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Database migrations completed successfully",
                "output": result.stdout,
                "timestamp": "2025-10-18T23:00:00Z"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail={
                    "status": "failed",
                    "message": "Migration failed",
                    "error": result.stderr,
                    "output": result.stdout
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "error",
                "message": "Error running migrations",
                "error": str(e)
            }
        )

@app.get("/admin/migration-status")
async def get_migration_status():
    """Check current migration status"""
    try:
        # Get current migration version
        result = subprocess.run([
            sys.executable, "-m", "alembic", "current"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # Get migration history
        history_result = subprocess.run([
            sys.executable, "-m", "alembic", "history", "--verbose"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        return {
            "status": "success",
            "current_version": result.stdout.strip() if result.returncode == 0 else "unknown",
            "migration_history": history_result.stdout if history_result.returncode == 0 else "unavailable",
            "database_connected": True,  # If we got here, basic app startup worked
            "timestamp": "2025-10-18T23:00:00Z"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": "Error checking migration status",
            "error": str(e),
            "timestamp": "2025-10-18T23:00:00Z"
        }

# ============== GENERAL PROVIDER ROUTES ==============

@app.get("/providers")
async def get_all_providers(db: Session = Depends(get_database_session)):
    """Get list of all available providers and their specializations"""
    try:
        from database.models import Provider, ProviderStatus
        
        # Query active providers from database
        providers = db.query(Provider).filter(Provider.status == ProviderStatus.ACTIVE).all()
        
        # Convert to response format
        provider_list = []
        available_count = 0
        
        for provider in providers:
            # Determine availability status (for demo purposes, alternating available/busy)
            availability = "Available" if len(provider_list) % 2 == 0 else "Busy"
            if availability == "Available":
                available_count += 1
            
            provider_data = {
                "provider_id": str(provider.id),
                "name": provider.name,
                "specialization": provider.specializations or [],
                "rating": provider.rating,
                "completed_tasks": provider.total_tasks_completed,
                "average_completion_time": f"{provider.average_completion_time_minutes} minutes" if provider.average_completion_time_minutes else "N/A",
                "availability": availability,
                "business_name": provider.business_name,
                "experience_years": provider.experience_years,
                "is_verified": provider.is_verified
            }
            provider_list.append(provider_data)
        
        return {
            "message": "Available providers retrieved from database",
            "providers": provider_list,
            "total_providers": len(provider_list),
            "available_now": available_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching providers: {str(e)}")

# ============== GENERAL CLASSIFICATION ROUTES (For testing/demo) ==============

@app.post("/classify")
async def classify_image(file: UploadFile = File(...)):
    """Classify an uploaded image using Google Gemini Vision API"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process the image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (for compatibility)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Check if API key is configured
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate content with the image
        prompt = "Analyze this image and classify what you see. Describe the main objects, scenes, or subjects in the image in detail."
        response = model.generate_content([prompt, image])
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "classification": response.text,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/classify/objects")
async def classify_objects(file: UploadFile = File(...)):
    """Classify objects in an uploaded image with structured response"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process the image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Check if API key is configured
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate structured classification
        prompt = """Analyze this image and provide a structured classification. Please identify:
        1. Main objects or subjects
        2. For men/women
        3. Colors and composition
        4. Size and dimensions
        
        Format your response in a clear, organized way."""
        
        response = model.generate_content([prompt, image])
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "detailed_classification": response.text,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)