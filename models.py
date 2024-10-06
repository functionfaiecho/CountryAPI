from bson import ObjectId
from pydantic import BaseModel, Field

# Custom Pydantic ObjectId class
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        
        return {"type": "string"}

    @classmethod
    def validate(cls, v, field=None, config=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

# Model for the destination
class DestinationModel(BaseModel):
    id: str = Field(default_factory=str, alias="_id")
    Destination: str
    Country: str
    Description: str
    Link: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
