from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any

from database.database import get_database_session
from database.models import Provider
from outfit-generation.outfit_generator import outfit_generator

# Create router for customer routes
router = APIRouter(prefix="/customer", tags=["Customer"])




@router.post("/post-prompt")
async def post_prompt(requestBody):
    outfit_generator



