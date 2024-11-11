from collections.abc import AsyncGenerator
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
from app.core.config import settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

load_dotenv()

DATABASE_URL = f"{settings.DB_DRIVER}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"         

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        future=True
    )
    factory = async_sessionmaker(
        engine,
        expire_on_commit=True,
        future=True
    )
    
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError as error:
            await session.rollback()
            raise
        
metadata = MetaData()
Base = declarative_base(metadata=metadata)