from .jwt_handler import decode_jwt

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()    

def validate_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_jwt(token)
    return payload