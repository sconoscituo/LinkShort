from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, HttpUrl
from app.database import get_db
from app.models.link import Link
from app.models.click_log import ClickLog
from app.models.user import User
from app.utils.auth import get_current_user, get_optional_user
from app.services.shortener import create_unique_code
from app.services.url_analyzer import analyze_url
from app.config import settings

router = APIRouter(prefix="/api/links", tags=["links"])


class LinkCreate(BaseModel):
    original_url: str
    custom_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    password: Optional[str] = None


class LinkResponse(BaseModel):
    id: int
    short_code: str
    original_url: str
    title: Optional[str]
    summary: Optional[str]
    category: Optional[str]
    clicks: int
    short_url: str
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LinkStats(BaseModel):
    total_clicks: int
    clicks_by_device: dict
    clicks_by_country: dict
    recent_clicks: List[dict]


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: LinkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    if current_user and not current_user.is_premium:
        count_result = await db.execute(
            select(func.count()).where(Link.user_id == current_user.id)
        )
        link_count = count_result.scalar()
        if link_count >= settings.FREE_LINKS_LIMIT:
            raise HTTPException(status_code=403, detail=f"Free plan limited to {settings.FREE_LINKS_LIMIT} links. Upgrade to premium.")

    if payload.custom_code:
        existing = await db.execute(select(Link).where(Link.short_code == payload.custom_code))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Custom code already in use")
        short_code = payload.custom_code
    else:
        short_code = await create_unique_code(db)

    title, summary, category = await analyze_url(payload.original_url)

    password_hash = None
    if payload.password:
        from app.utils.auth import get_password_hash
        password_hash = get_password_hash(payload.password)

    link = Link(
        user_id=current_user.id if current_user else None,
        original_url=payload.original_url,
        short_code=short_code,
        title=title,
        summary=summary,
        category=category,
        expires_at=payload.expires_at,
        password_hash=password_hash,
    )
    db.add(link)
    if current_user:
        current_user.total_links += 1
    await db.commit()
    await db.refresh(link)

    result = link.__dict__.copy()
    result["short_url"] = f"{settings.BASE_URL}/{short_code}"
    return result


@router.get("/", response_model=List[LinkResponse])
async def list_links(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Link).where(Link.user_id == current_user.id).offset(skip).limit(limit)
    )
    links = result.scalars().all()
    return [
        {**l.__dict__, "short_url": f"{settings.BASE_URL}/{l.short_code}"}
        for l in links
    ]


@router.get("/{link_id}/stats", response_model=LinkStats)
async def get_link_stats(
    link_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Link).where(Link.id == link_id, Link.user_id == current_user.id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    logs_result = await db.execute(
        select(ClickLog).where(ClickLog.link_id == link_id).order_by(ClickLog.created_at.desc()).limit(100)
    )
    logs = logs_result.scalars().all()

    clicks_by_device = {}
    clicks_by_country = {}
    for log in logs:
        device = log.device or "Unknown"
        country = log.country or "Unknown"
        clicks_by_device[device] = clicks_by_device.get(device, 0) + 1
        clicks_by_country[country] = clicks_by_country.get(country, 0) + 1

    return {
        "total_clicks": link.clicks,
        "clicks_by_device": clicks_by_device,
        "clicks_by_country": clicks_by_country,
        "recent_clicks": [
            {"created_at": str(log.created_at), "country": log.country, "device": log.device}
            for log in logs[:10]
        ],
    }


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Link).where(Link.id == link_id, Link.user_id == current_user.id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    await db.delete(link)
    await db.commit()
