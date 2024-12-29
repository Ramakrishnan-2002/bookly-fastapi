from fastapi import APIRouter,Depends,status,HTTPException
from ..database import db_dependency
from ..models import Book
from ..schemas import BookResponseData,BookCreateData
from datetime import datetime,timezone
from ..OAuth2 import get_current_user

router=APIRouter(
    prefix="/books",tags=['books']
)

@router.get("/",response_model=list[BookResponseData],status_code=status.HTTP_200_OK)
async def get_all_books(db:db_dependency):
    books=db.query(Book).all()
    if books is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found")
    return books


@router.get("/{book_id}",response_model=BookResponseData,status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id:int,db:db_dependency,user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised user")
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found")
    return book



@router.get("/getcuruserbook",response_model=list[BookResponseData],status_code=status.HTTP_200_OK)
async def get_current_user_book(db:db_dependency,user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised user")
    book = db.query(Book).filter(Book.user_id==user.id).first()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found")
    return book


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_book(book_data:BookCreateData,db:db_dependency,user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised user")
    book=Book(user_id=user.id,**book_data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
 
@router.delete("/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def del_book(book_id:int,db:db_dependency,user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised user")
    book = db.query(Book).filter(Book.user_id==user.id).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found")
    db.delete(book)
    db.commit()

@router.put("/{book_id}",status_code=status.HTTP_200_OK)
async def update_book(book_id:int,book_data:BookCreateData,db:db_dependency,user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised user")
    book = db.query(Book).filter(Book.user_id==user.id).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found")
    book.author=book_data.author
    book.title=book_data.title
    book.page_count=book_data.page_count
    book.created_at=datetime.now(timezone.utc)
    db.add(book)
    db.commit()
    db.refresh(book)
