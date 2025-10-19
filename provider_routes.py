from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import google.generativeai as genai
from PIL import Image
import io
import json
import os
from datetime import datetime
from typing import Dict, Any
import uuid

from database.models import InventoryItem, Provider
from database.database import get_database_session
from google.cloud import storage

# Create router for provider routes
router = APIRouter(prefix="/provider", tags=["Provider"])

# I need an endpoint to update the provider
@router.put("/update/{provider_id}")
async def update_provider(provider_id: str, provider_data: Dict[str, Any], db: Session = Depends(get_database_session)):
    """Update provider information"""
    try:
        # Find the specific provider by ID
        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider with ID {provider_id} not found")
        
        # Update provider fields based on provided data
        for key, value in provider_data.items():
            if hasattr(provider, key):
                setattr(provider, key, value)
        
        # Update the updated_at timestamp
        provider.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(provider)
        
        return {
            "message": "Provider information updated successfully",
            "provider_id": str(provider.id),
            "updated_fields": list(provider_data.keys()),
            "timestamp": datetime.now().isoformat() + "Z",
            "user_type": "provider"
        }
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating provider information: {str(e)}")

@router.post("/upload-inventory")
async def upload_inventory(file: UploadFile = File(...), db: Session = Depends(get_database_session)):
    """
    Provider uploads inventory images to extract product details.
    Uses AI to analyze the image and extract:
    - Product name and description
    - Category classification
    - Key features and specifications
    - Condition assessment
    - Estimated pricing suggestions
    """
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
        
        # Configure Google Generative AI with API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        genai.configure(api_key=api_key)
        
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Comprehensive inventory analysis prompt
        prompt = """
        Analyze this product image and extract detailed inventory information. Provide a comprehensive analysis in the following JSON format:

        {
            "product_name": "Clear, descriptive product name",
            "category": "Primary product category",
            "subcategory": "More specific subcategory",
            "description": "Detailed product description",
            "key_features": ["feature1", "feature2", "feature3"],
            "brand": "Brand name if visible",
            "model_number": "Model/SKU if visible",
            "condition": "New/Used/Refurbished assessment",
            "condition_notes": "Specific condition observations",
            "dimensions_estimate": "Estimated size description",
            "color": "Primary color(s)",
            "material": "Material type if identifiable",
            "estimated_price_range": {
                "min": "Minimum estimated price in EUR",
                "max": "Maximum estimated price in EUR",
                "currency": "EUR"
            },
            "marketability_score": "1-10 rating for market appeal",
            "tags": ["tag1", "tag2", "tag3"],
            "additional_notes": "Any other relevant observations"
        }

        Be thorough and professional in your analysis. If certain information cannot be determined from the image, indicate "Not visible/determinable" for that field.
        """
        
        response = model.generate_content([prompt, image])
        
        # Try to parse the AI response as JSON, fallback to text if needed
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            inventory_data = json.loads(response_text)

            # Get first provider from providers table
            # Let's assume we
            provider = db.query(Provider).first()
            provider_id = provider.id
            
            # Create inventory item with proper field mapping
            inventory_item = InventoryItem(
                id=uuid.uuid4(),
                provider_id=provider_id,
                product_name=inventory_data.get("product_name", "Unknown Product"),
                description=inventory_data.get("description", ""),
                category=inventory_data.get("category", ""),
                subcategory=inventory_data.get("subcategory", ""),
                brand=inventory_data.get("brand", ""),
                model_number=inventory_data.get("model_number", ""),
                condition=inventory_data.get("condition", ""),
                condition_notes=inventory_data.get("condition_notes", ""),
                dimensions_estimate=inventory_data.get("dimensions_estimate", ""),
                color=inventory_data.get("color", ""),
                material=inventory_data.get("material", ""),
                # Handle price range
                estimated_price_min=float(inventory_data.get("estimated_price_range", {}).get("min", 0)) if inventory_data.get("estimated_price_range", {}).get("min", "").replace(".", "").isdigit() else None,
                estimated_price_max=float(inventory_data.get("estimated_price_range", {}).get("max", 0)) if inventory_data.get("estimated_price_range", {}).get("max", "").replace(".", "").isdigit() else None,
                currency=inventory_data.get("estimated_price_range", {}).get("currency", "EUR"),
                marketability_score=float(inventory_data.get("marketability_score", 0)) if str(inventory_data.get("marketability_score", "")).replace(".", "").isdigit() else None,
                # Store arrays and additional data
                key_features=inventory_data.get("key_features", []),
                tags=inventory_data.get("tags", []),
                ai_analysis_raw=inventory_data,  # Store the full AI response
                # Image information
                original_filename=file.filename,
                image_content_type=file.content_type,
                analyzed_at=datetime.utcnow()
            )
            
            # Save to database
            try:
                db.add(inventory_item)
                db.commit()
                db.refresh(inventory_item)
                inventory_id = str(inventory_item.id)
            except Exception as db_error:
                db.rollback()
                # Continue without database save if there's an error
                print(f"Database save failed: {db_error}")
                inventory_id = str(uuid.uuid4())

            # Upload the image to Google Cloud Storage; use the provider ID and inventory ID for path
            try:
                # Configure Google Cloud Storage client
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
                
                if project_id:
                    gcs_client = storage.Client(project=project_id)
                else:
                    # On Cloud Run, this should work without explicit project ID
                    # For local development, ensure gcloud auth application-default login is done
                    gcs_client = storage.Client()
                
                bucket_name = os.getenv("GCS_BUCKET")
                if not bucket_name:
                    raise Exception("Google Cloud Storage bucket not configured")
                
                bucket = gcs_client.bucket(bucket_name)
                
                # Create storage path using provider ID and inventory ID
                file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
                storage_path = f"inventory/{provider_id}/{inventory_id}{file_extension}"
                
                # Create a blob (file) in the bucket
                blob = bucket.blob(storage_path)
                
                # Reset image data stream position and prepare for upload
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='JPEG', quality=85, optimize=True)
                image_bytes.seek(0)
                
                # Set metadata
                blob.metadata = {
                    'provider_id': str(provider_id),
                    'inventory_id': inventory_id,
                    'original_filename': file.filename or 'unknown'
                }
                
                # Upload to Google Cloud Storage
                blob.upload_from_file(
                    image_bytes,
                    content_type='image/jpeg'
                )
                
                # Make the blob publicly readable (optional - depends on your security requirements)
                # blob.make_public()
                
                # Generate public URL
                image_url = f"https://storage.googleapis.com/{bucket_name}/{storage_path}"
                
                # Update inventory item with image URL
                inventory_item.image_url = image_url
                inventory_item.storage_path = storage_path
                db.add(inventory_item)
                db.commit()
                
                print(f"Image uploaded successfully to Google Cloud Storage: {image_url}")
                
            except Exception as upload_error:
                print(f"Image upload failed: {upload_error}")
                # Continue without failing the entire operation
                inventory_item.image_url = None
                inventory_item.storage_path = None
                
                # Still commit the inventory item without the image
                try:
                    db.add(inventory_item)
                    db.commit()
                except Exception as db_error:
                    print(f"Database update after upload failure also failed: {db_error}")
                    db.rollback()


        except (json.JSONDecodeError, AttributeError):
            # Fallback if JSON parsing fails - generate a simple ID
            inventory_id = str(uuid.uuid4())
            inventory_data = {
                "raw_analysis": response.text,
                "parsed": False,
                "note": "AI response could not be parsed as structured JSON"
            }
        
        return {
            "inventory_id": inventory_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "upload_timestamp": datetime.now().isoformat() + "Z",
            "analysis_status": "completed",
            "extracted_data": inventory_data,
            "provider_action": "inventory_upload",
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing inventory image: {str(e)}")

@router.get("/inventories")
async def get_provider_inventory(db: Session = Depends(get_database_session)):
    """Get provider's inventory list from database"""
    try:
        # Get all inventory items from database with provider information
        inventory_items = db.query(InventoryItem).join(Provider).all()

        
        items = []
        for item in inventory_items:
            items.append({
                "inventory_id": str(item.id),
                "product_name": item.product_name,
                "category": item.category,
                "description": item.description,
                "condition": item.condition,
                "marketability_score": item.marketability_score,
                "image_url": item.image_url,
                "upload_date": item.created_at.isoformat() + "Z" if item.created_at else None,
                "status": item.status.value if item.status else "active",
                "provider_name": item.provider.name,
                "business_address": item.provider.business_address,
                "business_address_map_url": f"https://maps.google.com/maps?q={item.provider.business_address.replace(' ', '+')}" if item.provider.business_address else None,
            })
        
        return {
            "message": "Provider inventory retrieved from database",
            "inventory_items": items,
            "total_items": len(items),
            "user_type": "provider"
        }
    except Exception as e:
        # Fallback to sample data if database fails
        return {
            "message": "Provider inventory retrieved (sample data - database error)",
            "inventory_items": [
                {
                    "inventory_id": "inv_001",
                    "product_name": "Sample Product 1",
                    "category": "Electronics",
                    "upload_date": "2025-01-18T10:00:00Z",
                    "status": "active"
                }
            ],
            "total_items": 1,
            "user_type": "provider",
            "error": str(e)
        }

@router.get("/inventory/{inventory_id}")
async def get_inventory_item_details(inventory_id: str):
    """Get detailed information for a specific inventory item"""
    return {
        "inventory_id": inventory_id,
        "product_name": "Sample Product Details",
        "category": "Electronics",
        "description": "Detailed product description",
        "upload_date": "2025-01-18T10:00:00Z",
        "analysis_data": {
            "condition": "New",
            "estimated_price": {"min": 50, "max": 75, "currency": "USD"},
            "marketability_score": 8
        },
        "status": "active",
        "user_type": "provider"
    }

@router.put("/inventory/{inventory_id}")
async def update_inventory_item(inventory_id: str, update_data: Dict[str, Any]):
    """Update inventory item details"""
    return {
        "message": f"Inventory item {inventory_id} updated successfully",
        "inventory_id": inventory_id,
        "updated_fields": list(update_data.keys()),
        "timestamp": datetime.now().isoformat() + "Z",
        "user_type": "provider"
    }

@router.delete("/inventory/{inventory_id}")
async def delete_inventory_item(inventory_id: str, db: Session = Depends(get_database_session)):
    """Delete an inventory item"""
    try:
        # Find the inventory item by ID
        inventory_item = db.query(InventoryItem).filter(InventoryItem.id == inventory_id).first()
        
        if not inventory_item:
            raise HTTPException(status_code=404, detail=f"Inventory item {inventory_id} not found")
        
        # Store item details for response before deletion
        item_name = inventory_item.product_name
        storage_path = inventory_item.storage_path
        
        # Delete the inventory item from database
        db.delete(inventory_item)
        db.commit()
        
        # Optionally delete the image from Google Cloud Storage
        if storage_path:
            try:
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
                bucket_name = os.getenv("GCS_BUCKET")
                
                if bucket_name:
                    if project_id:
                        gcs_client = storage.Client(project=project_id)
                    else:
                        gcs_client = storage.Client()
                    
                    bucket = gcs_client.bucket(bucket_name)
                    blob = bucket.blob(storage_path)
                    
                    # Delete the blob if it exists
                    if blob.exists():
                        blob.delete()
                        print(f"Image deleted from Google Cloud Storage: {storage_path}")
                    
            except Exception as gcs_error:
                print(f"Warning: Could not delete image from storage: {gcs_error}")
                # Continue even if image deletion fails
        
        return {
            "message": f"Inventory item '{item_name}' deleted successfully",
            "inventory_id": inventory_id,
            "deleted_at": datetime.now().isoformat() + "Z",
            "user_type": "provider"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting inventory item: {str(e)}")
