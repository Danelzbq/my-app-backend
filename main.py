"""
FastAPI backend application for managing posts, favorites, and user browsing history.

Provides RESTful API endpoints for:
- User authentication (register/login)
- Post management (CRUD operations)
- Favorite posts
- Browsing history tracking
"""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import models
import schemas
import database
import auth

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Initialize FastAPI application
app = FastAPI(
    title="Blog API",
    description="API for managing blog posts, favorites, and user browsing history",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"msg": "hello"}

# Add CORS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

# If wildcard is used, credentials must be False for browsers to accept it.
allow_credentials = False if "*" in allowed_origins else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- User Auth ---
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Register a new user with username and password.
    
    Returns user_id and username on success.
    Raises 400 error if username already exists.
    """
    # Check if username already exists
    db_user = db.query(models.User).filter(
        models.User.username == login_data.username
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already registered"
        )
    
    # Hash password and create user
    hashed_password = auth.get_password_hash(login_data.password)
    db_user = models.User(
        username=login_data.username, 
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "message": "Registration successful", 
        "user_id": db_user.id, 
        "username": db_user.username
    }

@app.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with username and password.
    
    Returns user_id and username on success.
    Raises 401 error if credentials are invalid.
    """
    # Find user by username
    user = db.query(models.User).filter(
        models.User.username == login_data.username
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Verify password
    if not auth.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    return {
        "message": "Login successful", 
        "user_id": user.id, 
        "username": user.username
    }

# --- Posts APIs ---

@app.post("/posts/", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
def create_post(
    post: schemas.PostCreate, 
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Create a new post.
    
    Supports two ways to specify the owner:
    1. owner_id in request body (PostCreate schema)
    2. user_id as query parameter (for compatibility)
    
    Requires post details including title, content, author, etc.
    Returns the created post with generated ID and timestamp.
    """
    # Support user_id query parameter for backward compatibility
    post_data = post.model_dump()
    if user_id is not None:
        post_data['owner_id'] = user_id
    
    db_post = models.Post(**post_data)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of posts with pagination.
    
    Args:
        skip: Number of posts to skip (default: 0)
        limit: Maximum number of posts to return (default: 100)
    
    Returns list of posts ordered by creation date (newest first).
    """
    posts = db.query(models.Post)\
        .order_by(models.Post.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single post by ID.
    
    Raises 404 error if post doesn't exist.
    """
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post not found"
        )
    return post

@app.get("/users/{user_id}/posts", response_model=List[schemas.Post])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all posts created by a specific user.
    
    Returns posts ordered by creation date (newest first).
    """
    posts = db.query(models.Post)\
        .filter(models.Post.owner_id == user_id)\
        .order_by(models.Post.created_at.desc())\
        .all()
    return posts

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Update an existing post by ID.

    Optionally verifies owner via user_id query parameter.
    """
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if user_id is not None and post.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to edit this post"
        )

    update_data = post_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return post

@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Delete a post by ID.

    Optionally verifies owner via user_id query parameter.
    """
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if user_id is not None and post.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this post"
        )

    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}

# --- Favorites APIs ---

@app.post("/favorites/", status_code=status.HTTP_201_CREATED)
def add_favorite(user_id: int, post_id: int, db: Session = Depends(get_db)):
    """
    Add a post to user's favorites.
    
    Returns 201 if favorite added, 200 if already favorited.
    Raises 404 if post doesn't exist.
    """
    # Verify post exists
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post not found"
        )

    # Check if already favorited
    existing = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.post_id == post_id
    ).first()

    if existing:
        return {
            "message": "Already favorited", 
            "favorite_id": existing.id
        }

    # Create new favorite
    favorite = models.Favorite(user_id=user_id, post_id=post_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return {
        "message": "Favorite added", 
        "favorite_id": favorite.id
    }

@app.delete("/favorites/")
def remove_favorite(user_id: int, post_id: int, db: Session = Depends(get_db)):
    """
    Remove a post from user's favorites.
    
    Raises 404 if favorite doesn't exist.
    """
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.post_id == post_id
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Favorite not found"
        )

    db.delete(favorite)
    db.commit()
    return {"message": "Favorite removed"}

@app.get("/users/{user_id}/favorites", response_model=List[schemas.Post])
def get_user_favorites(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all posts favorited by a user.
    
    Returns posts ordered by favorite creation date (newest first).
    """
    # Get favorite records
    favorites = db.query(models.Favorite)\
        .filter(models.Favorite.user_id == user_id)\
        .order_by(models.Favorite.created_at.desc())\
        .all()
    
    # Extract post IDs and fetch posts
    post_ids = [f.post_id for f in favorites]
    if not post_ids:
        return []
    
    # Create a dict for quick lookup and maintain order
    posts = db.query(models.Post).filter(models.Post.id.in_(post_ids)).all()
    posts_dict = {p.id: p for p in posts}
    ordered_posts = [posts_dict[pid] for pid in post_ids if pid in posts_dict]
    
    return ordered_posts

@app.get("/favorites/check")
def check_favorite(user_id: int, post_id: int, db: Session = Depends(get_db)):
    """
    Check if a post is favorited by a user.
    
    Returns boolean indicating favorite status.
    """
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.post_id == post_id
    ).first()
    return {"is_favorited": favorite is not None}

# --- Browsing History APIs ---

@app.post("/browsing-history/", status_code=status.HTTP_201_CREATED)
def add_browsing_history(user_id: int, post_id: int, db: Session = Depends(get_db)):
    """
    Add or update a browsing history record.
    
    If the user has already viewed this post, updates the viewed time.
    Otherwise, creates a new browsing history record.
    """
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Verify post exists
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post not found"
        )
    
    # Check for existing browsing history
    existing = db.query(models.BrowsingHistory).filter(
        models.BrowsingHistory.user_id == user_id,
        models.BrowsingHistory.post_id == post_id
    ).first()
    
    if existing:
        # Delete old record to update with new timestamp
        db.delete(existing)
        db.commit()
    
    # Create new browsing history record
    history = models.BrowsingHistory(user_id=user_id, post_id=post_id)
    db.add(history)
    db.commit()
    db.refresh(history)
    
    return {
        "message": "Browsing history updated", 
        "history_id": history.id
    }


@app.get("/users/{user_id}/browsing-history", response_model=List[schemas.Post])
def get_user_browsing_history(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve user's browsing history.
    
    Returns posts ordered by view time (most recent first).
    Raises 404 if user doesn't exist.
    """
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Query browsing history ordered by view time
    history_records = db.query(models.BrowsingHistory)\
        .filter(models.BrowsingHistory.user_id == user_id)\
        .order_by(models.BrowsingHistory.viewed_at.desc())\
        .all()
    
    # Get corresponding posts maintaining browsing order
    post_ids = [h.post_id for h in history_records]
    if not post_ids:
        return []
    
    posts = db.query(models.Post).filter(models.Post.id.in_(post_ids)).all()
    posts_dict = {p.id: p for p in posts}
    ordered_posts = [posts_dict[pid] for pid in post_ids if pid in posts_dict]
    
    return ordered_posts


@app.delete("/browsing-history/")
def clear_browsing_history(user_id: int, db: Session = Depends(get_db)):
    """
    Clear all browsing history for a user.
    
    Returns the number of records deleted.
    Raises 404 if user doesn't exist.
    """
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Delete all browsing history for user
    deleted_count = db.query(models.BrowsingHistory)\
        .filter(models.BrowsingHistory.user_id == user_id)\
        .delete()
    db.commit()
    
    return {
        "message": f"Cleared {deleted_count} browsing history records"
    }
