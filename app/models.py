from .database import Base
from sqlalchemy import Integer,String,Column,func,ForeignKey,TIMESTAMP,Boolean
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__="users"
    id = Column(Integer,primary_key=True,index=True,nullable=False)
    username=Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True)
    is_verified=Column(Boolean,default=False)
    role=Column(String,nullable=False)
    password=Column(String,nullable=False)
    ph_number=Column(Integer,nullable=False,unique=True)
    created_at=Column(TIMESTAMP(timezone=True),nullable=True,server_default=func.now())

class Book(Base):
    __tablename__="books"
    id=Column(Integer,primary_key=True,index=True,nullable=False)
    title=Column(String,nullable=False)
    author=Column(String,nullable=False)
    page_count=Column(Integer,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=True,server_default=func.now())
    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    user=relationship("User")
    
