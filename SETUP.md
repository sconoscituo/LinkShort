# LinkShort - 프로젝트 설정 가이드

## 프로젝트 소개

LinkShort는 URL 단축 서비스로, Google Gemini AI를 활용한 링크 분석 기능을 제공하는 SaaS 서비스입니다. 무료 플랜(최대 10개 링크)과 프리미엄 플랜(무제한)을 지원하며, User-Agent 파싱을 통한 접속 통계를 제공합니다.

- **기술 스택**: FastAPI, SQLAlchemy (asyncio), SQLite, Google Gemini AI
- **인증**: JWT 7일 만료
- **무료 한도**: 링크 10개

---

## 필요한 API 키 / 환경변수

| 환경변수 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini AI API 키 | [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `SECRET_KEY` | JWT 서명용 비밀 키 | 직접 생성 (`openssl rand -hex 32`) |
| `BASE_URL` | 서비스 기본 URL (기본: `http://localhost:8000`) | - |
| `DATABASE_URL` | DB 연결 URL (기본: SQLite) | - |
| `DEBUG` | 디버그 모드 (기본: `false`) | - |
| `FREE_LINKS_LIMIT` | 무료 링크 최대 개수 (기본: `10`) | - |
| `PREMIUM_PRICE_USD` | 프리미엄 가격 USD (기본: `9.99`) | - |

---

## GitHub Secrets 설정 방법

저장소의 **Settings > Secrets and variables > Actions** 에서 아래 Secrets를 등록합니다.

```
GEMINI_API_KEY     = <Google AI Studio에서 발급한 키>
SECRET_KEY         = <openssl rand -hex 32 으로 생성한 값>
BASE_URL           = <배포 서버 URL>
```

---

## 로컬 개발 환경 설정

### 1. 저장소 클론

```bash
git clone https://github.com/sconoscituo/LinkShort.git
cd LinkShort
```

### 2. Python 가상환경 생성 및 의존성 설치

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경변수 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
BASE_URL=http://localhost:8000
DATABASE_URL=sqlite+aiosqlite:///./linkshort.db
DEBUG=true
FREE_LINKS_LIMIT=10
PREMIUM_PRICE_USD=9.99
```

---

## 실행 방법

### 로컬 실행 (uvicorn)

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서 확인: [http://localhost:8000/docs](http://localhost:8000/docs)

### Docker Compose로 실행

```bash
docker-compose up --build
```

### 테스트 실행

```bash
pytest tests/
```
