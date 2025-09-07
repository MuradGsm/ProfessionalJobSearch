from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr
from sqlalchemy import func
from sqlalchemy.pool import QueuePool
from typing import Annotated
from datetime import datetime
from app.config.setting import settings

engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True,  
    pool_size=20,        
    max_overflow=30,      
    pool_timeout=30,      
    pool_recycle=3600,    
    pool_pre_ping=True,   
    poolclass=QueuePool
)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

pk_int = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(default=func.now())]
updated_at = Annotated[datetime, mapped_column(default=func.now(), onupdate=func.now())]

class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f'{cls.__name__.lower()}'
    
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]