from fastapi import APIRouter, HTTPException, Depends, Request
from database import destination_collection
from models import DestinationModel
from auth import verify_admin
from typing import List
from bson import ObjectId  # Import to check and handle ObjectIds
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

# Instantiate the APIRouter for the destination routes
router = APIRouter()

# Create an instance of Limiter to apply rate limiting
limiter = Limiter(key_func=get_remote_address)

# Helper function to convert ObjectId to string
def convert_object_id(destination):
    # If a destination has an ObjectId, convert it to a string for JSON serialization
    if destination and "_id" in destination:
        destination["_id"] = str(destination["_id"])
    return destination

# Add a root route that returns a welcome message
@router.get("/")
def read_root():
    return {"message": "Welcome to CountriesAPI! Use /docs for API documentation."}

# Search destinations by Destination, Country, or Description - The public can do this.
@router.get("/destinations/search", response_model=List[DestinationModel])
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def search_destinations(request: Request, destination: str = None, country: str = None, description: str = None):
    # Build a dynamic query based on the provided search fields
    query = {}
    if destination:
        query["Destination"] = {"$regex": destination, "$options": "i"}  # Case-insensitive search on Destination
    if country:
        query["Country"] = {"$regex": country, "$options": "i"}  # Case-insensitive search on Country
    if description:
        query["Description"] = {"$regex": description, "$options": "i"}  # Case-insensitive search on Description

    # Find destinations that match the query, limited to 100 results
    results = await destination_collection.find(query).to_list(100)

    # Raise an HTTP 404 error if no matching destinations are found
    if not results:
        raise HTTPException(status_code=404, detail="No destinations found")

    # Convert ObjectId to string for each destination in the result
    return [convert_object_id(result) for result in results]

# Get all destinations (Public access)
@router.get("/destinations", response_model=List[DestinationModel])
@limiter.limit("20/minute")  # Rate limit: 20 requests per minute
async def get_destinations(request: Request):
    # Fetch all destinations from the database, limited to 1000 results
    destinations = await destination_collection.find().to_list(1000)
    # Convert ObjectId to string for each destination
    return [convert_object_id(destination) for destination in destinations]

# Get a specific destination by ID (Public access)
@router.get("/destinations/{id}", response_model=DestinationModel)
@limiter.limit("15/minute")  # Rate limit: 15 requests per minute
async def get_destination(request: Request, id: str):
    # Find a destination by its ObjectId
    destination = await destination_collection.find_one({"_id": ObjectId(id)})
    # Raise an HTTP 404 error if the destination is not found
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
    # Raise an HTTP 404 error if the destination is not found
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
    # Raise an HTTP 404 error if the destination could not be deleted
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Destination not found")
    return {"message": "Destination deleted successfully"}  # Added a message to confirm deletion
