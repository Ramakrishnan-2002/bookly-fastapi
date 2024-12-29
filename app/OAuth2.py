from .schemas import TokenResponseData
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import status, HTTPException, Depends
from .database import db_dependency
from fastapi.security import OAuth2PasswordBearer
from .models import User
import redis
import secrets

# Initialize Redis client
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

# Constants
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = 'HS256'
TOKEN_EXPIRE_IN_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Create Access Token
def create_access_token(data: dict):
    payload = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_IN_MINUTES)
    payload.update({"exp": expires, "jti": secrets.token_hex(16)})  # Add unique JTI
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Create Refresh Token
def create_refresh_token(data: dict):
    payload = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expires, "jti": secrets.token_hex(16)})  # Add unique JTI
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Revoke Token
def revoke_token(jti: str, expires_in: int):
    """Revoke a token by storing its JTI in Redis with expiration."""
    try:
        redis_client.setex(jti, expires_in, "revoked")
    except redis.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to Redis for token revocation"
        )

# Check if Token is Revoked
def is_token_revoked(jti: str):
    """Check if a token's JTI exists in Redis."""
    return redis_client.get(jti) is not None

# Verify Access Token
def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if not jti:
            raise credential_exception

        # Check if token is revoked
        if is_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        id: str = payload.get("id")
        email: str = payload.get("email")

        if not id or not email:
            raise credential_exception
        token_data = TokenResponseData(id=id, email=email)
        return token_data
    except JWTError:
        raise credential_exception

# Dependency for OAuth2 Bearer Token
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/login/token', auto_error=False)

# Get Current User
def get_current_user(db: db_dependency, token: str = Depends(oauth2_bearer)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token"
    )
    try:
        token_data = verify_access_token(token, credential_exception=credential_exception)
        user = db.query(User).filter(User.id == token_data.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except JWTError:
        raise credential_exception

# Logout Endpoint to Revoke Token
def logout(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token does not contain a valid ID"
            )

        # Revoke the token
        exp = payload.get("exp")
        expires_in = int(exp - datetime.now(timezone.utc).timestamp())
        if expires_in <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has already expired and cannot be revoked"
            )

        revoke_token(jti, expires_in)

        return {"detail": "Token revoked successfully"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
