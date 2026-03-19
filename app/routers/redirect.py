import hashlib
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.link import Link
from app.models.click_log import ClickLog
from app.models.user import User
from app.utils.auth import verify_password

router = APIRouter(tags=["redirect"])


def detect_device(user_agent: str) -> str:
    ua = user_agent.lower()
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        return "Mobile"
    if "tablet" in ua or "ipad" in ua:
        return "Tablet"
    return "Desktop"


@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    password: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Link).where(Link.short_code == short_code, Link.is_active == True))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Link has expired")

    if link.password_hash:
        if not password or not verify_password(password, link.password_hash):
            raise HTTPException(status_code=401, detail="Password required or incorrect")

    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
    user_agent = request.headers.get("user-agent", "")
    referer = request.headers.get("referer")
    device = detect_device(user_agent)

    click_log = ClickLog(
        link_id=link.id,
        ip_hash=ip_hash,
        user_agent=user_agent[:512],
        country=None,
        device=device,
        referer=referer[:512] if referer else None,
    )
    db.add(click_log)
    link.clicks += 1

    if link.user_id:
        user_result = await db.execute(select(User).where(User.id == link.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.total_clicks += 1

    await db.commit()
    return RedirectResponse(url=link.original_url, status_code=302)
