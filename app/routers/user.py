from fastapi import APIRouter,status,BackgroundTasks
from fastapi.responses import JSONResponse

from app.mailer import create_message,mail
from ..database import db_dependency
from .. import models,utils
from ..schemas import PasswordResetRequestModel, UserCreate

from ..utils import create_url_safe_token

router=APIRouter(
    tags=['users'],
    prefix="/users"
)


@router.post("/createuser")
async def create_user(new_user : UserCreate,db:db_dependency,bg_tasks:BackgroundTasks):
    new_user.password=utils.hash(new_user.password)
    user_model= models.User(**new_user.model_dump())
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    #creating the verification token
    token=create_url_safe_token({"email":new_user.email})
    #send the token for verification via link
    link=f"http://localhost:8000/login/verify/{token}"
    # Email content
    html_message = f"""
    <h1>Verify Your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your account.</p>
    """

    message = create_message(
        recipients=[new_user.email], subject="Verify Your Email", body=html_message
    )
    bg_tasks.add_task(mail.send_message,message) #Instead of using await , we use background tasks which works faster in backgrnd

    return {"message": "User created successfully! Please verify your email."}


# Password Reset Request Endpoint
@router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel,bg_tasks:BackgroundTasks):
    email = email_data.email
    
    # Create token
    token = create_url_safe_token({"email": email})
    link = f"http://localhost:8000/login/password-reset-confirm/{token}"
    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href=\"{link}\">link</a> to Reset Your Password.</p>
    """

    # Send email
    message = create_message(
        recipients=[email], subject="Reset Your Password", body=html_message
    )
    bg_tasks.add_task(mail.send_message,message)

    return JSONResponse(
        content={"message": "Please check your email for instructions to reset your password."},
        status_code=status.HTTP_200_OK
    )