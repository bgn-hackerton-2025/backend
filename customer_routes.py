from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database.database import get_database_session
from database.schemas import InventorySearchRequest, InventorySearchResponse, InventoryItemWithProviderResponse
from database.crud import InventoryCRUD

# Create router for customer routes
router = APIRouter(prefix="/customer", tags=["Customer"])

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

        # Convert to response format and add provider information
        inventory_responses = []
        for item in matching_items:
            # Create the response object with provider information
            response_obj = InventoryItemWithProviderResponse.model_validate(item)
            response_obj.business_name = item.provider.business_name
            response_obj.business_address = item.provider.business_address
            response_obj.business_address_map_url = f"https://maps.google.com/maps?q={item.provider.business_address.replace(' ', '+')}" if item.provider.business_address else None
            inventory_responses.append(response_obj)

        return InventorySearchResponse(
            message=message,
            inventory_items=inventory_responses,
            total_matches=len(matching_items),
            query=q
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching inventory: {str(e)}")
