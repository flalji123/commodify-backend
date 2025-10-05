from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os, shutil

from .database import Base, engine
from .models import User, Company, Project, Task, Comment, TeamMembership, FileAsset, Activity
from .schemas import (
    RegisterIn, LoginIn, TokenOut,
    CompanyIn, CompanyOut,
    ProjectIn, ProjectOut, ProjectUpdate,
    TaskIn, TaskOut, TaskUpdate,
    CommentIn, CommentOut,
    TeamAddIn, TeamMemberOut,
    FileOut, ActivityOut, DDIn
)
from .auth import get_db, hash_pw as get_password_hash, verify_pw as verify_password, token as create_access_token, current_user

# ---------- DB ----------
Base.metadata.create_all(bind=engine)

# ---------- App ----------
app = FastAPI(title="Commodify Backend v2")

ALLOWED_ORIGINS = [
    "https://flalji123.github.io",  # your Pages origin
    "https://flalji123.github.io/commodify-dashboard"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Health ----------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------- Auth ----------
@app.post("/auth/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=payload.email, password_hash=get_password_hash(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    tok = create_access_token(user.email)
    return {"access_token": tok}

@app.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    tok = create_access_token(user.email)
    return {"access_token": tok}

# ---------- CRM ----------
@app.get("/companies", response_model=List[CompanyOut])
def list_companies(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.query(Company).filter(Company.created_by == user.id).order_by(Company.id.desc()).all()

@app.post("/companies", response_model=CompanyOut)
def create_company(payload: CompanyIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = Company(name=payload.name, country=payload.country or "", notes=payload.notes or "", created_by=user.id)
    db.add(c); db.commit(); db.refresh(c)
    return c

@app.delete("/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = db.query(Company).filter(Company.id == company_id, Company.created_by == user.id).first()
    if not c: raise HTTPException(404, "Not found")
    db.delete(c); db.commit()
    return {"ok": True}

# ---------- PROJECTS ----------
@app.get("/projects", response_model=List[ProjectOut])
def projects_list(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.query(Project).filter(Project.created_by == user.id).order_by(Project.id.desc()).all()

@app.post("/projects", response_model=ProjectOut)
def projects_create(p: ProjectIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    proj = Project(created_by=user.id, **p.model_dump())
    db.add(proj); db.commit(); db.refresh(proj)
    log(db, user.id, "created project", "project", proj.id, proj.id)
    return proj

@app.get("/projects/{pid}", response_model=ProjectOut)
def projects_get(pid: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    proj = db.query(Project).filter(Project.id == pid, Project.created_by == user.id).first()
    if not proj: raise HTTPException(404, "Not found")
    return proj

@app.put("/projects/{pid}", response_model=ProjectOut)
def projects_update(pid: int, payload: ProjectUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    proj = db.query(Project).filter(Project.id == pid, Project.created_by == user.id).first()
    if not proj: raise HTTPException(404, "Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(proj, k, v if v is not None else getattr(proj, k))
    db.add(proj); db.commit(); db.refresh(proj)
    log(db, user.id, "updated project", "project", proj.id, proj.id)
    return proj

@app.delete("/projects/{pid}")
def projects_delete(pid: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    proj = db.query(Project).filter(Project.id == pid, Project.created_by == user.id).first()
    if not proj: raise HTTPException(404, "Not found")
    # cascade manually: tasks/comments/files/team
    db.query(Comment).filter(Comment.task_id.in_(db.query(Task.id).filter(Task.project_id == pid))).delete(synchronize_session=False)
    db.query(Task).filter(Task.project_id == pid).delete(synchronize_session=False)
    db.query(FileAsset).filter(FileAsset.project_id == pid).delete(synchronize_session=False)
    db.query(TeamMembership).filter(TeamMembership.project_id == pid).delete(synchronize_session=False)
    db.delete(proj); db.commit()
    log(db, user.id, "deleted project", "project", pid, pid)
    return {"ok": True}

# ---------- TASKS ----------
@app.get("/projects/{pid}/tasks", response_model=List[TaskOut])
def tasks_list(pid: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _ensure_project(pid, db, user)
    return db.query(Task).filter(Task.project_id == pid).order_by(Task.id.desc()).all()

@app.post("/projects/{pid}/tasks", response_model=TaskOut)
def tasks_create(pid: int, t: TaskIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _ensure_project(pid, db, user)
    row = Task(project_id=pid, created_by=user.id, **t.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    log(db, user.id, "created task", "task", row.id, pid)
    return row

@app.get("/tasks/{tid}", response_model=TaskOut)
def tasks_get(tid: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = _task_for_user(tid, db, user)
    return row

@app.put("/tasks/{tid}", response_model=TaskOut)
def tasks_update(tid: int, payload: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = _task_for_user(tid, db, user)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v if v is not None else getattr(row, k))
    db.add(row); db.commit(); db.refresh(row)
    log(db, user.id, "updated task", "task", row.id, row.project_id)
    return row

@app.delete("/tasks/{tid}")
def tasks_delete(tid: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = _task_for_user(tid, db, user)
    db.query(Comment).filter(Comment.task_id == tid).delete(synchronize_session=False)
    db.delete(row); db.commit()
    log(db, user.id, "deleted task", "task", tid, row.project_id)
    return {"ok": True}

# ---------- COMMENTS ----------
@app.get("/tasks/{tid}/comments", response_model=List[CommentOut])
def comments_list(tid: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _task_for_user(tid, db, user)
    return db.query(Comment).filter(Comment.task_id == tid).order_by(Comment.id.asc()).all()

@app.post("/tasks/{tid}/comments", response_model=CommentOut)
def comments_create(tid: int, c: CommentIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    t = _task_for_user(tid, db, user)
    row = Comment(task_id=tid, author_id=user.id, body=c.body)
    db.add(row); db.commit(); db.refresh(row)
    log(db, user.id, "commented", "task", tid, t.project_id)
    return row

# ---------- TEAM ----------
@app.get("/projects/{pid}/team", response_model=List[TeamMemberOut])
def team_list(pid: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _ensure_project(pid, db, user)
    return db.query(TeamMembership).filter(TeamMembership.project_id == pid).all()

@app.post("/projects/{pid}/team", response_model=TeamMemberOut)
def team_add(pid: int, payload: TeamAddIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _ensure_project(pid, db, user)
    row = TeamMembership(project_id=pid, user_id=payload.user_id, role=payload.role or "Member")
    db.add(row); db.commit(); db.refresh(row)
    log(db, user.id, "added member", "project", pid, pid)
    return row

@app.delete("/projects/{pid}/team/{member_id}")
def team_remove(pid: int, member_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _ensure_project(pid, db, user)
    row = db.query(TeamMembership).filter(TeamMembership.id == member_id, TeamMembership.project_id == pid).first()
    if not row: raise HTTPException(404, "Not found")
    db.delete(row); db.commit()
    log(db, user.id, "removed member", "project", pid, pid)
    return {"ok": True}

# ---------- FILES (metadata; stored under /tmp/uploads) ----------
UPLOAD_DIR = "/tmp/commodify_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/projects/{pid}/files", response_model=FileOut)
async def files_upload(pid: int, f: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(current_user)):
    _ensure_project(pid, db, user)
    # Save to ephemeral storage (Render free dynos reset on redeploy)
    dest = os.path.join(UPLOAD_DIR, f.filename)
    with open(dest, "wb") as out:
        shutil.copyfileobj(f.file, out)
    size = os.path.getsize(dest)
    row = FileAsset(project_id=pid, filename=f.filename, size=size, path=dest, uploaded_by=user.id)
    db.add(row); db.commit(); db.refresh(row)
    log(db, user.id, "uploaded file", "file", row.id, pid)
    return row

@app.get("/projects/{pid}/files", response_model=List[FileOut])
def files_list(pid: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _ensure_project(pid, db, user)
    return db.query(FileAsset).filter(FileAsset.project_id == pid).order_by(FileAsset.id.desc()).all()

# ---------- Activity ----------
@app.get("/activity", response_model=List[ActivityOut])
def activity_feed(limit: int = 50, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.query(Activity).order_by(Activity.id.desc()).limit(limit).all()

# ---------- Due Diligence (mock) ----------
@app.post("/duediligence")
def due_diligence(payload: DDIn, user: User = Depends(current_user)):
    score = (len(payload.name) * 13) % 100
    return {
        "name": payload.name,
        "country": payload.country,
        "risk_score": score,
        "flags": ["sanctions_check: clear", "whois: n/a", "adverse_media: low"]
    }

# ---------- Helpers ----------
def _ensure_project(pid: int, db: Session, user: User) -> Project:
    proj = db.query(Project).filter(Project.id == pid, Project.created_by == user.id).first()
    if not proj: raise HTTPException(404, "Project not found")
    return proj

def _task_for_user(tid: int, db: Session, user: User) -> Task:
    row = db.query(Task).filter(Task.id == tid).first()
    if not row: raise HTTPException(404, "Task not found")
    proj = _ensure_project(row.project_id, db, user)
    return row

def log(db: Session, actor_id: int, verb: str, object_type: str, object_id: int, project_id: int | None):
    db.add(Activity(actor_id=actor_id, verb=verb, object_type=object_type, object_id=object_id, project_id=project_id))
    db.commit()
