from pydantic import BaseModel, EmailStr
from typing import Optional, List

# -------- Auth --------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# -------- CRM --------
class CompanyIn(BaseModel):
    name: str
    country: Optional[str] = ""
    notes: Optional[str] = ""

class CompanyOut(CompanyIn):
    id: int
    model_config = {"from_attributes": True}

# -------- Projects --------
class ProjectIn(BaseModel):
    title: str
    description: Optional[str] = ""
    client: Optional[str] = ""
    status: Optional[str] = "Planning"
    priority: Optional[str] = "Medium"
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    client: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ProjectOut(ProjectIn):
    id: int
    model_config = {"from_attributes": True}

# -------- Tasks --------
class TaskIn(BaseModel):
    title: str
    description: Optional[str] = ""
    status: Optional[str] = "todo"
    progress: Optional[int] = 0
    priority: Optional[str] = "Normal"
    due_date: Optional[str] = ""
    assignee: Optional[int] = None
    parent_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    assignee: Optional[int] = None
    parent_id: Optional[int] = None

class TaskOut(TaskIn):
    id: int
    project_id: int
    model_config = {"from_attributes": True}

# -------- Comments --------
class CommentIn(BaseModel):
    body: str

class CommentOut(CommentIn):
    id: int
    task_id: int
    model_config = {"from_attributes": True}

# -------- Team --------
class TeamAddIn(BaseModel):
    user_id: int
    role: Optional[str] = "Member"

class TeamMemberOut(BaseModel):
    id: int
    user_id: int
    role: str
    model_config = {"from_attributes": True}

# -------- Files --------
class FileOut(BaseModel):
    id: int
    filename: str
    size: int
    model_config = {"from_attributes": True}

# -------- Activity --------
class ActivityOut(BaseModel):
    id: int
    verb: str
    object_type: str
    object_id: int
    project_id: int | None
    model_config = {"from_attributes": True}

# -------- Due Diligence --------
class DDIn(BaseModel):
    name: str
    country: Optional[str] = ""
