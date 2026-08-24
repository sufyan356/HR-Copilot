# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from jose import JWTError, jwt
# from fastapi import Depends, HTTPException
# from fastapi.security import OAuth2PasswordBearer

# from BACKEND.Config.config import SECRET_KEY,ALGORITHM

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)



# def create_token(id:int,email:str) -> str:
#     payload = {
#         "id": id,
#         "email": email,
#         "exp": datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
#     }
#     try:
#         encode = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     except JWTError as e:
#         raise e
#     return encode

# def verify_token(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from BACKEND.Config.config import SECRET_KEY,ALGORITHM

bearer_scheme = HTTPBearer()



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



def create_token(id:int,email:str) -> str:
    payload = {
        "id": id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    try:
        encode = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError as e:
        raise e
    return encode

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")