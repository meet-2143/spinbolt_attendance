import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import attendance, audit_logs, auth, dashboard, reports, supervisors
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("attendance")

settings = get_settings()

app = FastAPI(title="Attendance Management System API")

# Same-origin in production (frontend + /api share the Vercel domain), so this is
# only needed for local dev where Vite runs on a different port than uvicorn.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # Most routes raise HTTPException(detail="a string message"); a few (duplicate
    # attendance, bulk row errors) raise with a dict detail carrying extra fields
    # (existing_id, errors) alongside the message - both end up as {success, message, ...}.
    if isinstance(exc.detail, dict):
        content = {"success": False, **exc.detail}
    else:
        content = {"success": False, "message": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Something went wrong. Please try again."},
    )


app.include_router(auth.router)
app.include_router(supervisors.router)
app.include_router(attendance.router)
app.include_router(dashboard.router)
app.include_router(audit_logs.router)
app.include_router(reports.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
