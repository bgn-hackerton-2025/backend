from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai
from PIL import Image
import io
import json
import os
from datetime import datetime
from typing import Dict, Any
import uuid

# Create router for provider routes
router = APIRouter(prefix="/provider", tags=["Provider"])

@router.post("/upload-inventory")
async def upload_inventory(file: UploadFile = File(...)):
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
        
        # Generate unique inventory ID
        inventory_id = str(uuid.uuid4())
        
        # Try to parse the AI response as JSON, fallback to text if needed
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            inventory_data = json.loads(response_text)
        except (json.JSONDecodeError, AttributeError):
            # Fallback if JSON parsing fails
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

@router.get("/inventory")
async def get_provider_inventory():
    """Get provider's inventory list"""
    return {
        "message": "Provider inventory retrieved",
        "inventory_items": [
            {
                "inventory_id": "inv_001",
                "product_name": "Sample Product 1",
                "category": "Electronics",
                "upload_date": "2025-01-18T10:00:00Z",
                "status": "active"
            },
            {
                "inventory_id": "inv_002", 
                "product_name": "Sample Product 2",
                "category": "Furniture",
                "upload_date": "2025-01-18T11:00:00Z",
                "status": "active"
            }
        ],
        "total_items": 2,
        "user_type": "provider"
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
async def delete_inventory_item(inventory_id: str):
    """Delete an inventory item"""
    return {
        "message": f"Inventory item {inventory_id} deleted successfully",
        "inventory_id": inventory_id,
        "deleted_at": datetime.now().isoformat() + "Z",
        "user_type": "provider"
    }
