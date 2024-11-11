from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import List, Optional

async def get_user(db: AsyncSession, user_id: str) -> User:    
    result = await db.execute(select(User).where(User.id == user_id, User.active == True))
    user = result.scalars().first()      
    return user

async def get_user_deactivate(db: AsyncSession, user_id: str) -> User:    
    result = await db.execute(select(User).where(User.id == user_id, User.active == False))
    user = result.scalars().first()      
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> User:
    result = await db.execute(select(User).where(User.email == email, User.active == True))
    user = result.scalars().first()        
    return user

async def get_users(db: AsyncSession, offset: int, limit: int) -> List[User]:
    query = select(User).where(User.active == True).offset(offset).limit(limit)    
    result = await db.execute(query)        
    users = result.scalars().all()  
    return users 

async def create_user(db: AsyncSession, user: UserCreate) -> User:    
    db_user = User(
        name_complete=user.name_complete,
        email=user.email,
        role=user.role,
        password=user.password,  
        active=user.active     
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: str, user_data: UserUpdate):
    db_user = await get_user(db, user_id)
    if db_user:
        db_user.name_complete = user_data.name_complete
        db_user.email = user_data.email
        db_user.role = user_data.role
        db_user.active = user_data.active
        await db.commit()
        await db.refresh(db_user)
    return db_user

async def deactivate_user(db: AsyncSession, user_id: str) -> bool:
    db_user = await get_user(db, user_id)
    if not db_user:
        return False  
    db_user.active = 0  # Soft-delete
    await db.commit()
    await db.refresh(db_user)
    return True 

async def activate_user(db: AsyncSession, user_id: str) -> bool:
    db_user = await get_user_deactivate(db, user_id)
    if not db_user:
        return False  
    db_user.active = 1  # Soft-activate
    await db.commit()
    await db.refresh(db_user)
    return True 

async def filter_users(   
    db: AsyncSession,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None)        
) -> List[User]:
    
    result = await db.execute(select(User))
    all_users = result.scalars().all()

    users_dict = [{
        'id': str(user.id),
        'name_complete': user.name_complete,
        'email': user.email,
        'role': user.role.value,
    } for user in all_users]
    
    filtered_users = users_dict 

    if search:
        search_keywords = search.split()          
        for user in users_dict:
            name_complete = f"{user['name_complete']}".lower()
            email = f"{user['email']}".lower()
            role = f"{user['role']}".lower()
            if any(
                keyword.lower() in name_complete or 
                keyword.lower() in email.lower() or
                keyword.lower() in role.lower() for keyword in search_keywords):                
                filtered_users.append(user)            
        
        filtered_users = filtered_users

    total_users = len(filtered_users)
    paginated_users = filtered_users[offset:offset + limit]

    return {
        "total": total_users,
        "clients": paginated_users,
        "limit": limit,
        "offset": offset,
    }