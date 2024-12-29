from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import books,auth,user,admin,mail

app=FastAPI()

origins=["*"] #we can specify which domain we can use 


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(books.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(mail.router)