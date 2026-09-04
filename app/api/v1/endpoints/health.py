from fastapi import APIRouter, HTTPException, status

from app.db.session import check_database_connection

router = APIRouter(
    tags=["Health"],
)


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Application is running",
    }


@router.get("/ready")
async def readiness_check():
    try:
        await check_database_connection()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable",
        ) from exc

    return {
        "status": "ok",
        "database": "connected",
    }
