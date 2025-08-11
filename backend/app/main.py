from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import users, groups, sms, admin
import time
import json
import os

# Import logging configuration to initialize it
from app.core.logging import logger, safe_log

# Note: Database tables are now managed via Alembic migrations
# Run 'python db_manager.py migrate' to create/update tables

app = FastAPI(title="Group SMS Chat API")

# Log application startup (Windows-safe)
safe_log("info", "Starting Group SMS Chat API...")


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log incoming request
    logger.info(
        f"[IN] {request.method} {request.url.path} - "
        f"Client: {request.client.host}"
    )

    # Log query parameters if any
    if request.query_params:
        logger.debug(f"   Query params: {dict(request.query_params)}")

    # Log headers (excluding sensitive ones)
    headers_to_log = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in ["authorization", "cookie", "x-api-key"]
    }
    logger.debug(f"   Headers: {headers_to_log}")

    # For POST/PUT requests, try to log body (be careful with sensitive data)
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                # Try to parse as JSON for better formatting
                try:
                    body_json = json.loads(body.decode())
                    # Mask sensitive fields
                    if isinstance(body_json, dict):
                        masked_body = {
                            k: "***"
                            if k.lower() in ["password", "otp_code", "token"]
                            else v
                            for k, v in body_json.items()
                        }
                        logger.debug(
                            f"   Body: {json.dumps(masked_body, indent=2)}")
                    else:
                        logger.debug(f"   Body: {body_json}")
                except json.JSONDecodeError:
                    logger.debug(f"   Body (raw): {body.decode()[:200]}...")
        except Exception as e:
            logger.debug(f"   Could not read body: {e}")

    # Process the request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(
        f"[OUT] {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Time: {process_time:.3f}s"
    )

    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(sms.router, prefix="/api/sms", tags=["sms"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

safe_log("info", "All routers registered successfully")


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Group SMS Chat API"}


@app.get("/api/health")
def health_check():
    """Health check endpoint that also returns config info"""
    return {
        "status": "healthy",
        "mock_mode": os.getenv('MOCK_SMS', 'true').lower() == 'true'
    }
