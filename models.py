"""
Database models for the blog application.

Defines SQLAlchemy ORM models for users, posts, favorites, and browsing history.
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """User model for authentication and ownership."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Relationships
    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    browsing_history = relationship("BrowsingHistory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Post(Base):
    """Post model for blog articles and content."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), default="\u6587\u7ae0", nullable=False)
    title = Column(String(200), index=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(String(500), nullable=False)
    author = Column(String(100), nullable=False)
    tags = Column(String(200), nullable=True)
    cover_url = Column(String(500), nullable=True)
    image_urls = Column(Text, nullable=True)  # JSON string or comma-separated URLs
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="posts")
    favorites = relationship("Favorite", back_populates="post", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_posts_owner_created', 'owner_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title[:30]}...')>"


class Favorite(Base):
    """Favorite model for user's favorited posts."""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    post = relationship("Post", back_populates="favorites")
    
    # Indexes and constraints
    __table_args__ = (
        Index('ix_favorites_user_post', 'user_id', 'post_id', unique=True),
        Index('ix_favorites_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, post_id={self.post_id})>"


class BrowsingHistory(Base):
    """Browsing history model for tracking user's viewed posts."""
    __tablename__ = "browsing_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="browsing_history")
    post = relationship("Post")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('ix_history_user_viewed', 'user_id', 'viewed_at'),
        Index('ix_history_user_post', 'user_id', 'post_id'),
    )
    
    def __repr__(self):
        return f"<BrowsingHistory(user_id={self.user_id}, post_id={self.post_id})>"
