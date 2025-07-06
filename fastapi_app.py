from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv

from db_connect import db_manager

# Load environment variables
load_dotenv(".env")

# Pydantic models
class PingResult(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    url: str
    ip: str
    status: str
    response_time_ms: Optional[float]
    count: int

class PingResultCreate(BaseModel):
    url: str
    ip: str
    status: str
    response_time_ms: Optional[float]
    count: int

class URLStats(BaseModel):
    url: str
    total_pings: int
    successful_pings: int
    uptime_percentage: float
    avg_response_time: Optional[float]
    min_response_time: Optional[float]
    max_response_time: Optional[float]

# FastAPI lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_manager.initialize()
    yield
    # Shutdown
    await db_manager.close()

# Create FastAPI app
app = FastAPI(
    title="Ping Monitor API",
    description="API for monitoring ping results and network statistics",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/")
async def root():
    return {"message": "Ping Monitor API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        async with db_manager.get_connection() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e}")

@app.post("/ping-results/", response_model=dict)
async def create_ping_result(ping_result: PingResultCreate):
    """Create a new ping result"""
    try:
        result_id = await db_manager.insert_ping_result(
            url=ping_result.url,
            ip=ping_result.ip,
            status=ping_result.status,
            response_time=ping_result.response_time_ms,
            count=ping_result.count
        )
        return {"id": result_id, "message": "Ping result created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ping result: {e}")

@app.get("/env-config", response_model=Dict[str, Any])
async def serve_env_config():
    """Serve current .env configuration"""
    env_file = '.env'
    config = {}
    defaults = {
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': '',
        'SENDER_PASSWORD': '',
        'RECEIVER_EMAIL': '',
        'PING_THRESHOLD': '100',
        'ALERT_THRESHOLD': '3',
        'PING_INTERVAL': '10',
        'NOTIFICATION_TIMEOUT': '10',
        'CSV_FILENAME': 'ping_results.csv',
        'TARGET_URLS': 'g.co,github.com,microsoft.com',
        'ALERT_SOUND_FILE': 'alert.mp3'
    }

    # Load .env if exists
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    # Apply defaults
    for key, value in defaults.items():
        if key not in config:
            config[key] = value

    return config


@app.post("/env-config", response_model=Dict[str, str])
async def update_env_config(config_data: Dict[str, Any]):
    """Update .env configuration from posted data"""
    env_file = '.env'
    with open(env_file, 'w') as f:
        f.write("# SMTP Configuration\n")
        f.write(f"SMTP_SERVER={config_data.get('SMTP_SERVER', 'smtp.gmail.com')}\n")
        f.write(f"SMTP_PORT={config_data.get('SMTP_PORT', '587')}\n")
        f.write(f"SENDER_EMAIL={config_data.get('SENDER_EMAIL', '')}\n")
        f.write(f"SENDER_PASSWORD={config_data.get('SENDER_PASSWORD', '')}\n")
        f.write(f"RECEIVER_EMAIL={config_data.get('RECEIVER_EMAIL', '')}\n")
        f.write("\n# Ping Configuration\n")
        f.write(f"PING_THRESHOLD={config_data.get('PING_THRESHOLD', '100')}\n")
        f.write(f"ALERT_THRESHOLD={config_data.get('ALERT_THRESHOLD', '3')}\n")
        f.write(f"PING_INTERVAL={config_data.get('PING_INTERVAL', '10')}\n")
        f.write(f"NOTIFICATION_TIMEOUT={config_data.get('NOTIFICATION_TIMEOUT', '10')}\n")
        f.write("\n# Output File\n")
        f.write(f"CSV_FILENAME={config_data.get('CSV_FILENAME', 'ping_results.csv')}\n")
        f.write("\n# Target URLs\n")
        f.write(f"TARGET_URLS={config_data.get('TARGET_URLS', 'g.co,github.com,microsoft.com')}\n")
        f.write("\n# Alert Sound\n")
        f.write(f"ALERT_SOUND_FILE={config_data.get('ALERT_SOUND_FILE', 'alert.mp3')}\n")

    return {"status": "success", "message": "Configuration updated successfully"}


@app.get("/ping-results/", response_model=List[Dict[str, Any]])
async def get_ping_results(
    url: Optional[str] = Query(None, description="Filter by URL"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get ping results with optional filtering"""
    try:
        results = await db_manager.get_ping_results(url=url, limit=limit, offset=offset)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ping results: {e}")

# Alias for Flutter compatibility
@app.get("/ping-data", response_model=List[Dict[str, Any]])
async def get_ping_data(
    url: Optional[str] = Query(None, description="Filter by URL"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Get ping results (Flutter compatibility endpoint)"""
    return await get_ping_results(url=url, limit=limit, offset=offset)

@app.get("/latest-status/", response_model=List[Dict[str, Any]])
async def get_latest_status():
    """Get the latest status for each monitored URL"""
    try:
        status = await db_manager.get_latest_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest status: {e}")

@app.get("/statistics/{url}/", response_model=Dict[str, Any])
async def get_url_statistics(
    url: str,
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze")
):
    """Get statistics for a specific URL"""
    try:
        stats = await db_manager.get_url_statistics(url=url, hours=hours)
        if not stats:
            raise HTTPException(status_code=404, detail="No data found for this URL")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {e}")

@app.delete("/cleanup/")
async def cleanup_old_data(
    days_to_keep: int = Query(30, ge=1, le=365, description="Number of days to keep")
):
    """Clean up old ping results"""
    try:
        deleted_count = await db_manager.cleanup_old_data(days_to_keep=days_to_keep)
        return {"message": f"Cleaned up old data", "deleted_records": deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup data: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
