from fastapi import APIRouter, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Optional
import json

from database.database import get_database_session
from database.models import Provider
from database.schemas import outfitGeneratorRequest
from outfit_generation.outfit_generator import outfit_generator

# Create router for customer routes
router = APIRouter(prefix="/customer", tags=["Customer"])




@router.post("/outfits/recommendations")
async def post_prompt(requestBody: outfitGeneratorRequest, image: Optional[UploadFile] = File(None)):
    try:
        if requestBody:
            result = outfit_generator(requestBody, image)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



