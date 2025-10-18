from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any

from database.database import get_database_session
from database.models import Provider

# Create router for customer routes
router = APIRouter(prefix="/customer", tags=["Customer"])

@router.get("/profile")
async def get_customer_profile():
    """Get customer profile information"""
    return {
        "message": "Customer profile endpoint",
        "type": "customer",
        "status": "active",
        "services_available": ["image_classification", "product_identification", "custom_analysis"]
    }

@router.post("/upload-request")
async def customer_upload_request(file: UploadFile = File(...)):
    """Customer endpoint to upload images for classification requests"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique request ID
        request_id = f"req_{file.filename}_{hash(file.filename)}_{int(datetime.now().timestamp())}"
        
        return {
            "message": "Image upload request submitted",
            "filename": file.filename,
            "content_type": file.content_type,
            "request_id": request_id,
            "status": "pending",
            "estimated_completion": "Within 24 hours",
            "created_at": datetime.now().isoformat() + "Z",
            "user_type": "customer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

@router.get("/requests")
async def get_customer_requests():
    """Get all classification requests for customer"""
    return {
        "message": "Customer requests retrieved",
        "requests": [
            {
                "id": "req_001", 
                "filename": "product_image_1.jpg",
                "status": "completed", 
                "created_at": "2025-01-18T10:00:00Z",
                "completed_at": "2025-01-18T10:30:00Z",
                "provider_id": "prov_123"
            },
            {
                "id": "req_002", 
                "filename": "inventory_item_2.png",
                "status": "pending", 
                "created_at": "2025-01-18T11:30:00Z",
                "estimated_completion": "2025-01-18T17:30:00Z"
            },
            {
                "id": "req_003", 
                "filename": "document_scan.jpg",
                "status": "in_progress", 
                "created_at": "2025-01-18T12:15:00Z",
                "provider_id": "prov_456",
                "estimated_completion": "2025-01-18T14:15:00Z"
            }
        ],
        "total_requests": 3,
        "pending_requests": 1,
        "completed_requests": 1,
        "in_progress_requests": 1,
        "user_type": "customer"
    }

@router.get("/requests/{request_id}")
async def get_customer_request_detail(request_id: str):
    """Get specific request details for customer"""
    return {
        "request_id": request_id,
        "filename": "sample_image.jpg",
        "status": "completed",
        "classification_result": {
            "primary_classification": "Electronics - Smartphone",
            "confidence_score": 9.2,
            "detailed_analysis": "Apple iPhone 14 Pro in Space Black color. Device appears to be in excellent condition with no visible damage. Screen is clear and intact. All physical buttons and ports appear functional.",
            "features_detected": ["Touch screen", "Multiple cameras", "Lightning port", "Premium build quality"],
            "estimated_value": {"min": 800, "max": 950, "currency": "USD"},
            "condition": "Excellent",
            "marketability_score": 9.5
        },
        "provider_info": {
            "provider_id": "prov_123",
            "provider_name": "Tech Expert Solutions",
            "rating": 4.8,
            "specialization": "Electronics Classification"
        },
        "created_at": "2025-01-18T10:00:00Z",
        "completed_at": "2025-01-18T10:30:00Z",
        "processing_time": "30 minutes",
        "user_type": "customer"
    }

@router.post("/requests/{request_id}/feedback")
async def submit_request_feedback(request_id: str, feedback_data: Dict[str, Any]):
    """Submit feedback for a completed classification request"""
    return {
        "message": f"Feedback submitted for request {request_id}",
        "request_id": request_id,
        "feedback_received": True,
        "rating": feedback_data.get("rating"),
        "comments": feedback_data.get("comments"),
        "submitted_at": datetime.now().isoformat() + "Z",
        "user_type": "customer"
    }

@router.get("/pricing")
async def get_pricing_info():
    """Get current pricing information for classification services"""
    return {
        "message": "Current pricing information",
        "pricing_tiers": [
            {
                "tier": "Basic",
                "price": 5.00,
                "currency": "USD",
                "turnaround_time": "24-48 hours",
                "features": ["Basic classification", "Standard accuracy", "Text report"]
            },
            {
                "tier": "Premium", 
                "price": 12.00,
                "currency": "USD",
                "turnaround_time": "4-8 hours",
                "features": ["Detailed classification", "High accuracy", "Structured data", "Market analysis"]
            },
            {
                "tier": "Express",
                "price": 25.00, 
                "currency": "USD",
                "turnaround_time": "1-2 hours",
                "features": ["Priority processing", "Expert analysis", "Comprehensive report", "Price estimates"]
            }
        ],
        "user_type": "customer"
    }