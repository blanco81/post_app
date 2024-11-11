from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload, subqueryload
from app.models.post import Post, Tag
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from typing import List, Optional

async def get_posts(db: AsyncSession, offset: int, limit: int) -> List[Post]:
    query = (
        select(Post)
        .where(Post.deleted == False)
        .options(joinedload(Post.tags))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    posts = result.unique().scalars().all()  
    return posts

async def create_post(db: AsyncSession, post_data: PostCreate) -> Optional[PostResponse]:    
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        deleted=False,
        user_id=post_data.user_id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    if post_data.tag_names:
        tags = await get_or_create_tags(db, post_data.tag_names)
        new_post.tags.extend(tags)
        
    await db.commit()
    await db.refresh(new_post)
    
    stmt = select(Post).options(selectinload(Post.tags)).where(Post.id == new_post.id)
    result = await db.execute(stmt)
    new_post = result.scalar_one_or_none()
    
    return new_post 
    
async def get_or_create_tags(db: AsyncSession, tag_names: list) -> list:      
    existing_tags = await db.execute(select(Tag).where(Tag.name.in_(tag_names)))
    existing_tags = {tag.name: tag for tag in existing_tags.scalars().all()}

    new_tags = []
    for name in tag_names:
        if name not in existing_tags:
            new_tag = Tag(name=name)
            db.add(new_tag)
            new_tags.append(new_tag)
            
    return list(existing_tags.values()) + new_tags

async def get_post(db: AsyncSession, post_id: str) -> Post:
    result = await db.execute(select(Post).where(Post.id == post_id, Post.deleted == False).options(joinedload(Post.tags)))
    return result.scalars().first()

async def update_post(db: AsyncSession, post_id: str, post_data: PostUpdate) -> Optional[Post]:
    db_post = await get_post(db, post_id)
    
    if db_post:
        db_post.title = post_data.title
        db_post.content = post_data.content
        
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)

        if post_data.tag_names:
            tags = await get_or_create_tags(db, post_data.tag_names)
            db_post.tags.extend(tags)

        await db.commit()
        await db.refresh(db_post)
        
        stmt = select(Post).options(selectinload(Post.tags)).where(Post.id == db_post.id)
        result = await db.execute(stmt)
        db_post = result.scalar_one_or_none()
        
        return db_post
    else:
        return None  

async def delete_post(db: AsyncSession, post_id: str) -> bool:
    db_post = await get_post(db, post_id)
    if db_post:
        await Post.soft_delete(db, post_id)  
        #for tag in db_post.tags:
        #    await Tag.soft_delete(db, tag.id)        
        await db.commit()
        return True
    return False

async def get_all_tags(db: AsyncSession) -> List[Tag]:
    result = await db.execute(select(Tag).where(Tag.deleted == False))
    return result.scalars().all()


async def filter_posts(
    db: AsyncSession,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None)        
) -> dict:
    
    result = await db.execute(select(Post).options(subqueryload(Post.tags)).filter(Post.deleted == False))
    all_posts = result.scalars().all()
    posts_dict = [{
        'id': str(post.id),
        'title': post.title,
        'content': post.content,
        'user_id': post.user_id,
        'deleted': post.deleted,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
        'tags': [{'id': tag.id, 'name': tag.name} for tag in post.tags]
    } for post in all_posts]
    
    filtered_posts = posts_dict
    if search:
        search_keywords = search.split()
        filtered_posts = []

        for post in posts_dict:
            title = post['title'].lower()
            content = post['content'].lower()
            tags = " ".join([tag['name'].lower() for tag in post['tags']])
            if any(
                keyword.lower() in title or
                keyword.lower() in content or
                keyword.lower() in tags
                for keyword in search_keywords
            ):
                filtered_posts.append(post)
        
    total_posts = len(filtered_posts)
    paginated_posts = filtered_posts[offset:offset + limit]
    return {
        "total": total_posts,
        "posts": paginated_posts,
        "limit": limit,
        "offset": offset,
    }