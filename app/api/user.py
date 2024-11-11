# app/api/users.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import get_user, get_users, update_user, deactivate_user, activate_user, filter_users
from app.core.deps import get_db
from app.core.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/all", response_model=List[UserResponse])
async def read_users(    
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):    
    try:
        if current_user.role == UserRole.admin:   
            users = await get_users(db, offset=offset, limit=limit)
            users_response = [
                UserResponse(
                    id=user.id,
                    name_complete=user.name_complete,
                    email=user.email,
                    role=str(user.role.value),
                    active=user.active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )  
                for user in users
            ]
            return users_response
        else:
            raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error listing all users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@router.get("/show/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if current_user.role == UserRole.admin:    
            user = await get_user(db, user_id)    
            if user:
                # Crea y retorna la instancia de UserResponse directamente
                user_response = UserResponse(
                    id=user.id,
                    name_complete=user.name_complete,
                    email=user.email,
                    role=str(user.role.value),
                    active=user.active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )
                return user_response
            else:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error showing user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/edit/{user_id}", response_model=UserResponse)
async def edit_user(
    user_id: str,
    user: UserUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:        
        if current_user.role == UserRole.admin: 
            updated_user = await update_user(db, user_id, user)
             
            user_response = UserResponse(
                    id=user_id,
                    name_complete=updated_user.name_complete,
                    email=updated_user.email,
                    role=str(updated_user.role.value),
                    active=updated_user.active,
                    created_at=updated_user.created_at,
                    updated_at=updated_user.updated_at,
                )              
            
            return user_response
        else:
            raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/deactivate/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        if current_user.role == UserRole.admin:        
            user_deleted = await deactivate_user(db, user_id)          
        
            if user_deleted:
                return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error deactivating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/activate/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def activat_user(
    user_id: str, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        if current_user.role == UserRole.admin:        
            user_activate = await activate_user(db, user_id)           
        
            if user_activate:
                return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error activating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
@router.get("/filter")
async def filter_list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None)
):
    try:
        if current_user.role == UserRole.admin:        
            users_filters = await filter_users(db=db, limit=limit, offset=offset, search=search)
            return {"users": users_filters}
        else:
            raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        print(f"Error filtering users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")