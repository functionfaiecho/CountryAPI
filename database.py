import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection details from the .env file
MONGO_DETAILS = os.getenv("MONGO_DETAILS")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Create MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

# Get the specific database
database = client[MONGO_DB_NAME]

# Collection for destinations
destination_collection = database.get_collection("countries")
