from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image
import io
import json
import os
from database.models import Provider
from outfit_generation.outfit_generator import outfit_generator
from sqlalchemy.orm import Session
from database.database import get_database_session
from database.schemas import InventorySearchRequest, InventorySearchResponse, InventoryItemResponse, outfitGeneratorRequest
from database.crud import InventoryCRUD

# Create router for customer routes
router = APIRouter(prefix="/customer", tags=["Customer"])

@router.post("/recommendations")
async def post_prompt(
    requestBody: Optional[outfitGeneratorRequest]
):


    try:
        image_path = "imgs/input_image.png"

        # Check if the image file exists before trying to use it
        if os.path.exists(image_path):
            print(f"Found image at {image_path}")
            result = outfit_generator(requestBody, image_path)
        else:
            print("No image found — running prompt-only generation")
            result = outfit_generator(requestBody, None)

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...) 
):
    
    if os.path.exists("imgs/input_image.png"):
            try:
                os.remove("imgs/input_image.png")
                print(f"Cleaned up input image: \"imgs/input_image.png\"")
            except Exception as e:
                print(f"Error deleting input image: {str(e)}")

    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process the image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        os.makedirs("imgs", exist_ok=True)
        image_path = os.path.join("imgs", "input_image.png")
        image.save(image_path)

        return {"message": "✅ Image uploaded successfully", "path": image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@router.post("/search", response_model=InventorySearchResponse)
async def search_inventory(
    search_request: InventorySearchRequest,
    db: Session = Depends(get_database_session)
):
    """
    Keyword search over inventory description.
    - Accepts a single query string `q`.
    - Splits into words and matches all occurrences in `description`.
    - Returns best matches ranked by number of keyword hits.
    """
    try:
        q = search_request.query
        matching_items = InventoryCRUD.search_inventory(db, search_term=q, provider_id=None, limit=25)

        if not matching_items:
            matching_items = InventoryCRUD.get_random_inventory_items(db, limit=5)
            message = "No items matched your query. Here are some random items:"
        else:
            message = f"Found {len(matching_items)} matching items"

        inventory_responses = [InventoryItemResponse.model_validate(item) for item in matching_items]

        return InventorySearchResponse(
            message=message,
            inventory_items=inventory_responses,
            total_matches=len(matching_items),
            query=q
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching inventory: {str(e)}")
