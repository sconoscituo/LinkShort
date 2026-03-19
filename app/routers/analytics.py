"""
단축 링크 클릭 분석 라우터
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["링크 분석"])

try:
    from app.models.link import ShortLink
    HAS_LINK = True
except ImportError:
    HAS_LINK = False


@router.get("/links/{link_id}")
async def get_link_analytics(
    link_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """링크 클릭 통계"""
    if not HAS_LINK:
        return {"message": "링크 모델이 없습니다"}

    result = await db.execute(
        select(ShortLink).where(
            ShortLink.id == link_id,
            ShortLink.user_id == current_user.id
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(404, "링크를 찾을 수 없습니다")

    click_count = getattr(link, "click_count", 0) or 0
    created_at = getattr(link, "created_at", datetime.utcnow())
    days_active = max((datetime.utcnow() - created_at).days, 1)

    return {
        "link_id": link_id,
        "short_code": getattr(link, "short_code", ""),
        "original_url": getattr(link, "original_url", ""),
        "total_clicks": click_count,
        "days_active": days_active,
        "avg_daily_clicks": round(click_count / days_active, 2),
        "created_at": str(created_at),
    }


@router.get("/summary")
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """전체 링크 통계 요약"""
    if not HAS_LINK:
        return {"total_links": 0, "total_clicks": 0}

    result = await db.execute(
        select(
            func.count(ShortLink.id).label("total"),
            func.sum(ShortLink.click_count).label("clicks"),
        ).where(ShortLink.user_id == current_user.id)
    )
    row = result.one()
    return {
        "total_links": row.total or 0,
        "total_clicks": int(row.clicks or 0),
        "avg_clicks_per_link": round((row.clicks or 0) / max(row.total or 1, 1), 1),
    }
