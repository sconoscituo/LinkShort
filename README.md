# LinkShort

AI-powered URL shortener with click analytics.

## Features

- URL shortening with 6-character random codes
- Custom short code support
- Gemini AI: automatic title, summary, and category extraction
- Click analytics: count, device type, country, referer
- Link expiration and password protection
- JWT authentication
- Free (10 links) and Premium plans

## Quick Start

```bash
cp .env.example .env
# Edit .env with your settings

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/users/register | Register |
| POST | /api/users/login | Login |
| GET | /api/users/me | Profile |
| POST | /api/links/ | Create short link |
| GET | /api/links/ | List my links |
| GET | /api/links/{id}/stats | Click stats |
| DELETE | /api/links/{id} | Delete link |
| GET | /{short_code} | Redirect |
| GET | /api/payments/plans | View plans |
| POST | /api/payments/create | Create payment |
| POST | /api/payments/confirm | Confirm payment |

## Environment Variables

| Variable | Description |
|----------|-------------|
| DATABASE_URL | SQLite async URL |
| SECRET_KEY | JWT signing key |
| GEMINI_API_KEY | Google Gemini API key |
| BASE_URL | Public base URL for short links |
| FREE_LINKS_LIMIT | Max links for free users |
