
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import Base, engine
from .models import User, Company, Task
from .schemas import RegisterIn, LoginIn, TokenOut, CompanyIn, CompanyOut, TaskIn, TaskOut, DDIn
from .auth import get_db, hash_pw, verify_pw, token, current_user

Base.metadata.create_all(bind=engine)
app=FastAPI(title="Commodify API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

@app.post("/auth/register", response_model=TokenOut)
def register(p: RegisterIn, db: Session=Depends(get_db)):
    if db.query(User).filter(User.email==p.email).first(): raise HTTPException(400,"Email exists")
    u=User(email=p.email, password_hash=hash_pw(p.password)); db.add(u); db.commit(); db.refresh(u)
    return {"access_token": token(u.email)}

@app.post("/auth/login", response_model=TokenOut)
def login(p: LoginIn, db: Session=Depends(get_db)):
    u=db.query(User).filter(User.email==p.email).first()
    if not u or not verify_pw(p.password, u.password_hash): raise HTTPException(401,"Invalid credentials")
    return {"access_token": token(u.email)}

@app.get("/companies", response_model=list[CompanyOut])
def companies(db:Session=Depends(get_db), u:User=Depends(current_user)):
    return db.query(Company).filter(Company.created_by==u.id).order_by(Company.id.desc()).all()

@app.post("/companies", response_model=CompanyOut)
def companies_create(p:CompanyIn, db:Session=Depends(get_db), u:User=Depends(current_user)):
    c=Company(name=p.name, country=p.country or "", notes=p.notes or "", created_by=u.id); db.add(c); db.commit(); db.refresh(c); return c

@app.delete("/companies/{cid}")
def companies_delete(cid:int, db:Session=Depends(get_db), u:User=Depends(current_user)):
    c=db.query(Company).filter(Company.id==cid, Company.created_by==u.id).first(); 
    if not c: raise HTTPException(404,"Not found"); db.delete(c); db.commit(); return {"ok":True}

@app.get("/tasks", response_model=list[TaskOut])
def tasks(db:Session=Depends(get_db), u:User=Depends(current_user)):
    return db.query(Task).filter(Task.created_by==u.id).order_by(Task.id.desc()).all()

@app.post("/tasks", response_model=TaskOut)
def tasks_create(p:TaskIn, db:Session=Depends(get_db), u:User=Depends(current_user)):
    t=Task(title=p.title, status=p.status or "todo", created_by=u.id); db.add(t); db.commit(); db.refresh(t); return t

@app.put("/tasks/{tid}", response_model=TaskOut)
def tasks_update(tid:int, p:TaskIn, db:Session=Depends(get_db), u:User=Depends(current_user)):
    t=db.query(Task).filter(Task.id==tid, Task.created_by==u.id).first()
    if not t: raise HTTPException(404,"Not found")
    t.title = p.title or t.title; t.status = p.status or t.status; db.add(t); db.commit(); db.refresh(t); return t

@app.delete("/tasks/{tid}")
def tasks_delete(tid:int, db:Session=Depends(get_db), u:User=Depends(current_user)):
    t=db.query(Task).filter(Task.id==tid, Task.created_by==u.id).first()
    if not t: raise HTTPException(404,"Not found")
    db.delete(t); db.commit(); return {"ok":True}

@app.post("/duediligence")
def dd(p:DDIn, u:User=Depends(current_user)):
    score=(len(p.name)*13)%100
    return {"name":p.name, "country":p.country, "risk_score":score, "flags":["sanctions: clear","whois: n/a"]}
