from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.OAuth2 import create_access_token, create_refresh_token, verify_access_token
from ..database import db_dependency
from ..models import User
from ..utils import decode_url_safe_token, verify,hash
from ..schemas import PasswordResetConfirmModel, Token

router = APIRouter(
    prefix="/login",
    tags=['Authentication']
)

# Login Endpoint
@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login(
    user_cred: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    user = db.query(User).filter(user_cred.username == User.email).first()
    if not user or not verify(user_cred.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid credentials"
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not verified"
        )
    
    # Creating tokens
    access_token = create_access_token(data={"id": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"id": user.id, "email": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# Refresh Token Endpoint
@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=Token)
async def refresh_token(token: str):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid refresh token"
    )
    token_data = verify_access_token(token, credential_exception)

    # Generate a new access token
    new_access_token = create_access_token(data={"id": token_data.id, "email": token_data.email})
    new_refresh_token=token
    
    return {"access_token": new_access_token,"refresh_token": new_refresh_token, "token_type": "bearer"}


@router.get("/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, db: db_dependency):
    try:
        # Decode the token
        token_data = decode_url_safe_token(token)
        email = token_data.get("email")

        # Fetch the user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"message": "Account already verified"}

        # Mark user as verified
        user.is_verified = True
        db.commit()

        return {"message": "Account verified successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during verification")
    



# Password Reset Confirmation Endpoint
@router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str, 
    passwords: PasswordResetConfirmModel, 
    db: db_dependency
):
    # Validate passwords
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Passwords do not match"
        )
    
    # Decode token
    try:
        token_data = decode_url_safe_token(token)
        email = token_data.get("email")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid or expired token"
        )

    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    # if not user.is_verified:
    #         return {"message": "User not verified"}
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    # Update password
    user.password = hash(new_password)
    db.commit()
    db.refresh(user)

    return JSONResponse(
        content={"message": "Password reset successfully."},
        status_code=status.HTTP_200_OK
    )
