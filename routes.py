from fastapi import APIRouter, HTTPException, Depends, Request
from database import destination_collection
from models import DestinationModel
from auth import verify_admin
from typing import List
from bson import ObjectId  # To handle MongoDB ObjectIds
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

# Instantiate the APIRouter for the destination routes
router = APIRouter()

# Create an instance of Limiter to apply rate limiting
limiter = Limiter(key_func=get_remote_address)

# Helper function to convert ObjectId to string
# This ensures ObjectIds are properly serialised to strings before sending them to the client
def convert_object_id(destination):
    if destination and "_id" in destination:
        destination["_id"] = str(destination["_id"])
    return destination

# Root route to display a welcome message
@router.get("/")
def read_root():
    return {"message": "Welcome to CountriesAPI! Use /docs for API documentation."}

# Search destinations by destination name, country, or description - accessible by the public
@router.get("/destinations/search", response_model=List[DestinationModel])
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def search_destinations(request: Request, destination: str = None, country: str = None, description: str = None):
    # Build a dynamic query based on provided search fields (destination, country, or description)
    query = {}
    if destination:
        query["Destination"] = {"$regex": destination, "$options": "i"}  # Case-insensitive search on Destination
    if country:
        query["Country"] = {"$regex": country, "$options": "i"}  # Case-insensitive search on Country
    if description:
        query["Description"] = {"$regex": description, "$options": "i"}  # Case-insensitive search on Description

    # Find destinations matching the query, limit results to 100
    results = await destination_collection.find(query).to_list(100)

    # If no destinations are found, raise a 404 error
    if not results:
        raise HTTPException(status_code=404, detail="No destinations found")

    # Convert ObjectId to string for each destination
    return [convert_object_id(result) for result in results]

# Get all destinations, or filter by country/destination (Public access)
@router.get("/destinations", response_model=List[DestinationModel])
@limiter.limit("20/minute")  # Rate limit: 20 requests per minute
async def get_destinations(request: Request, country: str = None, destination: str = None):
    # Dynamically build the query if country or destination parameters are provided
    query = {}
    if country:
        query["Country"] = {"$regex": country, "$options": "i"}  # Case-insensitive search on Country
    if destination:
        query["Destination"] = {"$regex": destination, "$options": "i"}  # Case-insensitive search on Destination

    # Fetch destinations matching the query, limited to 1000 results
    destinations = await destination_collection.find(query).to_list(1000)

    # If no matching destinations are found, raise a 404 error
    if not destinations:
        raise HTTPException(status_code=404, detail="No destinations found for the given filters")

    # Convert ObjectId to string for each destination
    return [convert_object_id(destination) for destination in destinations]

# Get a specific destination by its ID (Public access)
@router.get("/destinations/{id}", response_model=DestinationModel)
@limiter.limit("15/minute")  # Rate limit: 15 requests per minute
async def get_destination(request: Request, id: str):
    # Find the destination by its ObjectId
    destination = await destination_collection.find_one({"_id": ObjectId(id)})

    # If the destination isn't found, raise a 404 error
    if destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    # Convert ObjectId to string
    return convert_object_id(destination)

# Create a new destination (Admin only)
@router.post("/destinations", response_model=DestinationModel)
@limiter.limit("5/minute")  # Rate limit: 5 requests per minute for creation (admin only)
async def create_destination(request: Request, destination: DestinationModel, username: str = Depends(verify_admin)):
    # Insert the new destination into the database
    result = await destination_collection.insert_one(destination.dict(by_alias=True))
    
    # Find and return the newly created destination by its ObjectId
    created_destination = await destination_collection.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string
    return convert_object_id(created_destination)

# Update a destination (Admin only)
@router.put("/destinations/{id}", response_model=DestinationModel)
@limiter.limit("5/minute")  # Rate limit: 5 requests per minute for updates (admin only)
async def update_destination(request: Request, id: str, destination: DestinationModel, username: str = Depends(verify_admin)):
    # Find and update the destination by its ObjectId
    updated_destination = await destination_collection.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": destination.dict(exclude_unset=True)}, return_document=True
    )
    
    # If the destination isn't found, raise a 404 error
    if updated_destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    # Convert ObjectId to string
    return convert_object_id(updated_destination)

# Delete a destination (Admin only)
@router.delete("/destinations/{id}", status_code=200)
@limiter.limit("3/minute")  # Rate limit: 3 delete requests per minute (admin only)
async def delete_destination(request: Request, id: str, username: str = Depends(verify_admin)):
    # Delete the destination by its ObjectId
    delete_result = await destination_collection.delete_one({"_id": ObjectId(id)})
    
    # If the destination couldn't be deleted, raise a 404 error
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    return {"message": "Destination deleted successfully"}  # Return a message confirming the deletion
