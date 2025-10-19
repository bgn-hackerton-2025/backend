from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List

from database.database import get_database_session
from database.models import Provider
from database.schemas import InventorySearchRequest, InventorySearchResponse, InventoryItemResponse
from database.crud import InventoryCRUD

# Create router for customer routes
router = APIRouter(prefix="/customer", tags=["Customer"])

@router.post("/search", response_model=InventorySearchResponse)
async def search_inventory(
    search_request: InventorySearchRequest,
    db: Session = Depends(get_database_session)
):
    """
    Search for inventory items based on multiple criteria.
    
    Required: category
    Optional: subcategory, color, style, aesthetic
    
    Returns weighted search results or 5 random items if no matches found.
    """
    try:
        # Perform weighted search
        matching_items = InventoryCRUD.weighted_search_inventory(db, search_request)
        
        # If no matches found, return 5 random items as fallback
        if not matching_items:
            matching_items = InventoryCRUD.get_random_inventory_items(db, limit=5)
            message = "No items found matching your criteria. Here are some random items from our inventory:"
        else:
            message = f"Found {len(matching_items)} items matching your search criteria"
        
        # Convert to response format
        inventory_responses = []
        for item in matching_items:
            inventory_responses.append(InventoryItemResponse.model_validate(item))
        
        return InventorySearchResponse(
            message=message,
            inventory_items=inventory_responses,
            total_matches=len(matching_items),
            search_criteria=search_request
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error searching inventory: {str(e)}"
        )
