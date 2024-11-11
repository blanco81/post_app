from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.tag import TagResponse

class PostBase(BaseModel):
    title: str
    content: str
    user_id: str

class PostCreate(PostBase):    
    tag_names: Optional[List[str]] = []

class PostUpdate(PostBase):
    user_id: Optional[str]
    tag_names: Optional[List[str]] = []

class PostResponse(PostBase):
    id: str
    user_id: str  
    deleted: bool
    created_at: Optional[datetime]  
    updated_at: Optional[datetime] 
    tags: List[TagResponse] 

    class Config:
        orm_mode = True
