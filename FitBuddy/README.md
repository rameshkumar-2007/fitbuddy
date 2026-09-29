# FitBuddy

FitBuddy is a FastAPI fitness-planning demo using Python, Jinja2, SQLite/SQLAlchemy, and Google's Gemini API. It creates goal-specific seven-day workout plans, nutrition and recovery tips, and plan revisions from feedback. The interface includes speech input and read-aloud when supported by the browser, locale selection, and visual exercise and meal references.

When Gemini is unavailable or over quota, the app provides a clearly labeled local starter plan. The local plan is not AI-generated. It supports muscle gain, weight loss, flexibility, and general wellness goals.

## Requirements

- Python 3.11 or newer
- A Gemini API key for AI-generated plans

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally. Set `GEMINI_API_KEY` to a key from Google AI Studio. Set `ADMIN_KEY` to a unique, long random value; admin access is disabled when it is empty. Never commit `.env` or paste API keys into issues or logs.

Run the app:

```powershell
py -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/>. Health status is available at `/health`; interactive API documentation is at `/docs`.

## Tests

```powershell
py -m pytest -q
```

GitHub Actions runs the test suite on pushes and pull requests.

## Admin access

The user dashboard and user-data API require HTTP Basic authentication with username `admin` and the `ADMIN_KEY` value as the password. Do not expose the development server publicly. Production deployments should use HTTPS, a production database, proper account-level authorization, request rate limits, and secret management.

## Project layout

```text
app/                  FastAPI routes, configuration, Gemini clients, and local fallback plans
static/               Styles and browser voice controls
templates/            Jinja2 pages and visual references
tests/                Route, fallback, and Gemini client tests
.env.example           Safe configuration template
.github/workflows/     GitHub Actions tests
```

FitBuddy is a wellness-planning demo, not a medical service. It does not diagnose conditions, prescribe medication, provide calorie targets, or recommend extreme dieting. Users under 18 receive lower-volume movement suggestions and non-restrictive nutrition guidance. Stop activity if pain, dizziness, or other concerning symptoms occur and seek appropriate help.