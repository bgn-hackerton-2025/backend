from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image
import io
import json
import os

from database.database import get_database_session
from database.models import Provider
from database.schemas import outfitGeneratorRequest
from outfit_generation.outfit_generator import outfit_generator

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






