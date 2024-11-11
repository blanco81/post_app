# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import AccessToken, LoginRequest, UserCreate, UserResponse
from app.services.user import get_user_by_email, create_user
from app.core.deps import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token



router = APIRouter()

@router.post("/login", response_model=AccessToken)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, login_data.email)    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not db_user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")    
    if not login_data.password == db_user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.email, "role": str(db_user.role)})    
    return AccessToken(access_token=access_token, token_type="Bearer")
    

@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):   
    try:
        existing_user = await get_user_by_email(db, user.email)
        if existing_user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Este e-mail ya está registrado."}
            )        
        new_user = UserCreate(
            name_complete=user.name_complete, 
            email=user.email, 
            password=user.password, 
            role=user.role,
            active=True)        
        new_user1 = await create_user(db, new_user)        
        return UserResponse(
            id=new_user1.id,
            name_complete=new_user1.name_complete,
            email=new_user1.email,
            role=str(new_user1.role.value),
            active=new_user1.active,
            created_at=new_user1.created_at,
            updated_at=new_user1.updated_at,
        )       
    
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/me", response_model=UserResponse)
async def get_current_user_data(    
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return UserResponse(
            id=current_user.id,
            name_complete=current_user.name_complete,
            email=current_user.email,
            role=str(current_user.role.value),
            active=current_user.active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
        )
    except Exception as e:
        print(f"Error fetching current user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/logout")
async def logout():
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Salida realizada"}
    )
    response.delete_cookie(key="access_token")
    return response

