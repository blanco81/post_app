# app/models/book.py
from app.core.deps import Base
from app.core.config import settings
from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from nanoid import generate
from sqlalchemy.orm import relationship
from app.utils.mixins import SoftDeleteMixin, TimestampMixin

key = settings.DB_SECRET_KEY

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", String(30), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(30), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class Post(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "posts"   
    
    id = Column(String(30), primary_key=True, default=generate)
    title = Column(String(200), index=True, nullable=False)    
    content = Column(Text)
    deleted = Column(Boolean, default=False)          
    user_id = Column(String(30), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="posts")        
    tags = relationship(
        'Tag',
        secondary=post_tags,
        lazy="selectin"  # Uso de selectin para carga diferida explícita
    )

class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id = Column(String(30), primary_key=True, default=generate)
    name = Column(String(200), unique=True, index=True)
    posts = relationship(
        'Post',
        secondary=post_tags,
        lazy="selectin",
        back_populates="tags"
    )