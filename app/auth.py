
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User

SECRET_KEY="CHANGE_ME"
ALGO="HS256"; EXP=60*24*7
pwd=CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth=OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()

def hash_pw(p): return pwd.hash(p)
def verify_pw(p,h): return pwd.verify(p,h)

def token(sub:str):
    payload={"sub":sub, "exp": datetime.utcnow()+timedelta(minutes=EXP)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def current_user(db:Session=Depends(get_db), tok:str=Depends(oauth))->User:
    try:
        data=jwt.decode(tok, SECRET_KEY, algorithms=[ALGO])
        email=data.get("sub")
    except JWTError:
        raise HTTPException(401,"Invalid token")
    u=db.query(User).filter(User.email==email).first()
    if not u: raise HTTPException(401,"Invalid user")
    return u
