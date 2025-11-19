"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any

# Example schemas (you can keep or remove if not used):

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Ascendia landing related schemas

class Message(BaseModel):
    """
    Contact messages collection
    Collection: "message"
    """
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    subject: Optional[str] = Field(None, max_length=180)
    message: str = Field(..., min_length=5, max_length=5000)

class AnalyticsEvent(BaseModel):
    """
    Analytics events collection
    Collection: "analyticsevent"
    """
    name: str = Field(..., description="Event name, e.g. page_view, cta_click")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class CheckoutSessionRequest(BaseModel):
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    amount_cents: int = Field(..., ge=50, description="Total amount in cents")
    currency: str = Field("usd", min_length=3, max_length=3)
    success_url: str
    cancel_url: str
