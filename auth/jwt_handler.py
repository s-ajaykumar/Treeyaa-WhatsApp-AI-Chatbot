import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
from config import JWT_SECRET_KEY
from fastapi import HTTPException, status



ALGORITHM = "HS256"

def decode_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms = [ALGORITHM])
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Token has expired"
        )
    except DecodeError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid token"
        )
