from fastapi import APIRouter,Depends,HTTPException,status
from ..schemas import UserOut,BookResponseData
from ..database import db_dependency
from ..OAuth2 import get_current_user
from ..models import User,Book

router=APIRouter(
    prefix="/admin",
    tags=['admin']
)

@router.get("/getallusers",response_model=list[UserOut])
async def get_all_users(db:db_dependency,user=Depends(get_current_user)):
    if user.role!='admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authorised to admin previleges")
    users=db.query(User).all()
    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Users not found")
    return users 
@router.get("/getallbooks",response_model=list[BookResponseData])
async def get_all_books(db:db_dependency,user=Depends(get_current_user)):
    if user.role!='admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authorised to admin previleges")
    books=db.query(Book).all()
    if books is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Books not found")
    return books