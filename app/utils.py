from passlib.context import CryptContext
pwd_context=CryptContext(schemes=['bcrypt'],deprecated="auto")


def hash(pwd:str):
    return pwd_context.hash(pwd)
def verify(pwd,hash_pwd):
    return pwd_context.verify(pwd,hash_pwd)

#To verify the user we are asking to verify
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired
from fastapi import HTTPException
import secrets
serializer=URLSafeTimedSerializer(secrets.token_hex(32),salt="email-configuration")


def create_url_safe_token(data:dict,expiration=3600):
    token=serializer.dumps(data)
    return token

def decode_url_safe_token(token:str,max_age=3600):
    try:
        data=serializer.loads(token,max_age=max_age)
        return data
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Token has expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid token")