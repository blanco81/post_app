from app.core.deps import Base
from app.core.config import settings
from enum import Enum as PyEnum
from sqlalchemy import Boolean, Column, String, Enum
from nanoid import generate
from sqlalchemy.orm import relationship
from sqlalchemy_utils import StringEncryptedType
from app.utils.mixins import TimestampMixin

key = settings.DB_SECRET_KEY

class UserRole(PyEnum):
    admin = "admin"
    editor = "editor"
    lector = "lector"
    

class User(Base, TimestampMixin):
    __tablename__ = "users"  
      
    id = Column(String(30), primary_key=True, default=generate)
    name_complete = Column(StringEncryptedType(String(200), key), nullable=False)
    email = Column(StringEncryptedType(String(200), key), unique=True, index=True, nullable=False)
    password = Column(StringEncryptedType(String(200), key), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    active = Column(Boolean, nullable=False, default=True)   
    posts = relationship("Post", back_populates="user")
    
    