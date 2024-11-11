from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from app.models.user import User, UserRole
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.schemas.tag import TagResponse
from app.services.post import create_post, get_post, get_posts, update_post, delete_post, filter_posts
from app.core.deps import get_db
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/all", response_model=List[PostResponse])
async def read_posts(    
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):    
    try:
        if current_user.role in [UserRole.admin, UserRole.editor, UserRole.lector]:
            posts = await get_posts(db, offset=offset, limit=limit)            
            posts_response = [
                PostResponse(
                    id=post.id,
                    title=post.title,  
                    content=post.content,  
                    tags=[TagResponse(id=tag.id, name=tag.name) for tag in post.tags],  
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    user_id=post.user_id,
                    deleted=post.deleted 
                )
                for post in posts
            ]            
            return posts_response
        else:
            raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error listing posts: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/create", response_model=PostResponse)
async def build_post(
    post: PostCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if current_user.role in [UserRole.admin, UserRole.editor]:
            post.user_id = current_user.id
            return await create_post(db, post)        
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error creating post for others, only can ADMIN and EDITOR : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
        
@router.get("/show/{post_id}", response_model=PostResponse)
async def read_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if current_user.role in [UserRole.admin, UserRole.editor, UserRole.lector]:
            post = await get_post(db, post_id=post_id)
            if post:
                return PostResponse(
                    id=post.id,
                    title=post.title,  
                    content=post.content,  
                    tags=[TagResponse(id=tag.id, name=tag.name) for tag in post.tags],  
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    user_id=post.user_id,
                    deleted=post.deleted 
                )
            raise HTTPException(status_code=404, detail="Post not found or deleted")
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error reading post: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/edit/{post_id}", response_model=PostResponse)
async def edit_post(
    post_id: str,
    post_data: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):    
    try:
        if current_user.role in [UserRole.admin, UserRole.editor]:            
            post = await get_post(db, post_id=post_id)            
            if post.user_id == current_user.id:            
                updated_post = await update_post(
                    db, 
                    post_id=post.id, 
                    post_data=post_data
                )
                if updated_post:  
                    return PostResponse(
                        id=updated_post.id,
                        title=updated_post.title,  
                        content=updated_post.content,  
                        tags=[TagResponse(id=tag.id, name=tag.name) for tag in updated_post.tags],  
                        created_at=updated_post.created_at,
                        updated_at=updated_post.updated_at,
                        user_id=updated_post.user_id,
                        deleted=updated_post.deleted 
                    )        
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error editing post for others, only can ADMIN and EDITOR : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        

@router.delete("/delete/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def erase_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if current_user.role in [UserRole.admin, UserRole.editor]:
            post_deleted = await delete_post(db, post_id=post_id)
            if post_deleted:
                return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error deleting post for others, only can ADMIN and EDITOR : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/filter")
async def search_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None)
):    
    if current_user.role in [UserRole.admin, UserRole.editor, UserRole.lector]:
        posts = await filter_posts(
            db, 
            limit=limit, 
            offset=offset, 
            search=search
        )
        return posts
        
