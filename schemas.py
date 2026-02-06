"""
Pydantic schemas for request/response validation.

Defines data validation schemas for API endpoints using Pydantic models.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=3, max_length=50, description="Username for authentication")


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=6, max_length=100, description="User password")


class User(UserBase):
    """Schema for user response."""
    id: int

    class Config:
        from_attributes = True


class AdminUser(UserBase):
    """Schema for admin user response."""
    id: int
    is_admin: bool

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    """Base post schema with common fields."""
    type: str = Field(default="文章", max_length=20)
    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, description="Post content")
    excerpt: str = Field(..., min_length=1, max_length=500, description="Post excerpt/summary")
    author: str = Field(..., min_length=1, max_length=100, description="Author name")
    tags: Optional[str] = Field(None, max_length=200, description="Comma-separated tags")
    cover_url: Optional[str] = Field(None, max_length=500, description="Cover image URL")
    image_urls: Optional[str] = Field(None, description="Image URLs (JSON or comma-separated)")
    
    @validator('title', 'content', 'excerpt', 'author')
    def strip_whitespace(cls, v):
        """Remove leading/trailing whitespace from text fields."""
        return v.strip() if v else v


class PostCreate(PostBase):
    """Schema for creating a new post."""
    owner_id: Optional[int] = Field(None, gt=0, description="ID of the post owner (can also use user_id query param)")


class PostUpdate(BaseModel):
    """Schema for updating an existing post."""
    type: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, min_length=1, max_length=500)
    tags: Optional[str] = Field(None, max_length=200)
    cover_url: Optional[str] = Field(None, max_length=500)
    image_urls: Optional[str] = None


class Post(PostBase):
    """Schema for post response."""
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
