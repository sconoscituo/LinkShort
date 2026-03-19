import httpx
import google.generativeai as genai
from typing import Optional, Tuple
from app.config import settings


def _init_gemini():
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel("gemini-1.5-flash")
    return None


async def fetch_page_title(url: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "LinkShort/1.0"})
            if resp.status_code == 200:
                content = resp.text[:5000]
                import re
                match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
                if match:
                    return match.group(1).strip()[:255]
    except Exception:
        pass
    return None


async def analyze_url(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Returns (title, summary, category) using Gemini AI.
    Falls back to title-only if Gemini is unavailable.
    """
    title = await fetch_page_title(url)

    model = _init_gemini()
    if not model:
        return title, None, None

    prompt = f"""Analyze this URL and provide:
1. A short title (max 10 words) if not already known: {title or 'unknown'}
2. A one-sentence summary of what the URL is about
3. A single category from: Technology, Business, News, Entertainment, Education, Health, Sports, Finance, Social, Other

URL: {url}

Respond in this exact format:
TITLE: <title>
SUMMARY: <one sentence summary>
CATEGORY: <category>"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        lines = {line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
                 for line in text.splitlines() if ":" in line}
        ai_title = lines.get("TITLE") or title
        summary = lines.get("SUMMARY")
        category = lines.get("CATEGORY")
        return ai_title, summary, category
    except Exception:
        return title, None, None
