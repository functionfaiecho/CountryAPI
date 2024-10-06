from fastapi import APIRouter, HTTPException, Depends
from database import destination_collection
from models import DestinationModel
from auth import verify_admin
from typing import List
from bson import ObjectId  # Import to check and handle ObjectIds

router = APIRouter()

# Helper function to convert ObjectId to string
def convert_object_id(destination):
    if destination and "_id" in destination:
        destination["_id"] = str(destination["_id"])
    return destination

# Search destinations by Destination, Country, or Description (Public access)
@router.get("/destinations/search", response_model=List[DestinationModel])
async def search_destinations(destination: str = None, country: str = None, description: str = None):
    # Build a dynamic query based on the provided search fields
    query = {}
    if destination:
        query["Destination"] = {"$regex": destination, "$options": "i"}  # Case-insensitive search on Destination
    if country:
        query["Country"] = {"$regex": country, "$options": "i"}  # Case-insensitive search on Country
    if description:
        query["Description"] = {"$regex": description, "$options": "i"}  # Case-insensitive search on Description

    # Find destinations that match the query, limit set to 100 results
    results = await destination_collection.find(query).to_list(100)

    # Raise error if no destinations match the search
    if not results:
        raise HTTPException(status_code=404, detail="No destinations found")

    # Convert ObjectId to string for each destination in the result
    return [convert_object_id(result) for result in results]

# Get all destinations (Public access)
@router.get("/destinations", response_model=List[DestinationModel])
async def get_destinations():
    # Fetch all destinations from the database, limit set to 1000
    destinations = await destination_collection.find().to_list(1000)
    # Convert ObjectId to string for each destination
    return [convert_object_id(destination) for destination in destinations]

# Get a specific destination by ID (Public access)
@router.get("/destinations/{id}", response_model=DestinationModel)
async def get_destination(id: str):
    # Find destination by ObjectId
    destination = await destination_collection.find_one({"_id": ObjectId(id)})
    # Raise error if destination is not found
    if destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    # Convert ObjectId to string
    return convert_object_id(destination)

# Create a new destination (Admin only)
@router.post("/destinations", response_model=DestinationModel)
async def create_destination(destination: DestinationModel, username: str = Depends(verify_admin)):
    # Insert the new destination into the collection
    result = await destination_collection.insert_one(destination.dict(by_alias=True))
    # Find the newly created destination by its inserted ObjectId
    created_destination = await destination_collection.find_one({"_id": result.inserted_id})
    # Convert ObjectId to string
    return convert_object_id(created_destination)

# Update a destination (Admin only)
@router.put("/destinations/{id}", response_model=DestinationModel)
async def update_destination(id: str, destination: DestinationModel, username: str = Depends(verify_admin)):
    # Find and update the destination by ObjectId
    updated_destination = await destination_collection.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": destination.dict(exclude_unset=True)}, return_document=True
    )
    # Raise error if destination is not found
    if updated_destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    # Convert ObjectId to string
    return convert_object_id(updated_destination)

# Delete a destination (Admin only)
@router.delete("/destinations/{id}", status_code=204)
async def delete_destination(id: str, username: str = Depends(verify_admin)):
    # Delete the destination by ObjectId
    delete_result = await destination_collection.delete_one({"_id": ObjectId(id)})
    # Raise error if the destination was not deleted
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Destination not found")
