# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🔧 If you organize endpoints as routers, import them here and uncomment the include lines below.
# Make sure these module paths match your repository structure.
# from .routers import auth, companies, projects, tasks, files, activity

app = FastAPI(
    title="Commodify API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------
# CORS (enables GitHub Pages UI to call this API on Render)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://flalji123.github.io",  # ✅ Your GitHub Pages origin (origin = scheme + host)
        # If you host on another domain later, add it here.
        # "https://your-custom-domain.com",
    ],
    allow_credentials=False,   # Using Bearer tokens (Authorization header), not cookies
    allow_methods=["*"],       # GET, POST, PUT, DELETE, PATCH, OPTIONS
    allow_headers=["*"],       # Authorization, Content-Type, etc.
)

# ---------------------------
# Optional: simple health check
# ---------------------------
@app.get("/health")
def health():
    return {"ok": True}

# ---------------------------
# Router includes
# ---------------------------
# Uncomment these and ensure the imports at top are correct for your project structure.
# app.include_router(auth.router,      prefix="/auth",     tags=["auth"])
# app.include_router(companies.router, prefix="/companies",tags=["companies"])
# app.include_router(projects.router,  prefix="/projects", tags=["projects"])
# app.include_router(tasks.router,     prefix="/tasks",    tags=["tasks"])
# app.include_router(files.router,     prefix="",          tags=["files"])      # if you mount /projects/{id}/files inside the router
# app.include_router(activity.router,  prefix="/activity", tags=["activity"])

# Note:
# - Keep your existing route definitions (if you define endpoints in this file, leave them here).
# - Do NOT duplicate endpoints (only one include/definition per path).

# No __main__ block is required for Render; it runs:
#   uvicorn app.main:app --host 0.0.0.0 --port $PORT
