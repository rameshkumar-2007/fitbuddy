import os
import re
from types import SimpleNamespace
import pytest
os.environ["DATABASE_URL"]="sqlite:///./test_fitbuddy.db"
os.environ["ADMIN_KEY"]="test-admin"
from fastapi.testclient import TestClient
from app.main import app
from app import gemini_client, gemini_flash_generator, gemini_generator, updated_plan
from app.starter_plan import build_starter_plan

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_health(client):
    r=client.get("/health"); assert r.status_code==200; assert r.json()["status"]=="ok"

def test_home(client):
    r=client.get("/"); assert r.status_code==200; assert "FitBuddy" in r.text; assert "User ID" not in r.text

def test_generate_and_update_plan_without_entering_user_id(client, monkeypatch):
    monkeypatch.setattr("app.routes.generate_workout_gemini", lambda *args: "Original plan")
    monkeypatch.setattr("app.routes.generate_nutrition_tip_with_flash", lambda *args: "Recovery tip")
    r=client.post("/generate-workout", data={"name":"Alex", "age":30, "weight":70, "goal":"general wellness", "intensity":"medium", "language":"es-ES"})
    assert r.status_code==200
    assert "User ID" not in r.text
    assert 'name="language" value="es-ES"' in r.text
    user_id=re.search(r'<input type="hidden" name="user_id" value="([^"]+)"', r.text).group(1)
    monkeypatch.setattr("app.routes.update_workout_plan", lambda *args: "Updated plan")
    updated=client.post("/submit-feedback", data={"user_id":user_id, "feedback":"Add more recovery"})
    assert updated.status_code==200
    assert "Updated plan" in updated.text

@pytest.mark.parametrize(("goal", "expected_day"), [
    ("muscle gain", "Upper-body strength"),
    ("weight loss", "Longer comfortable cardio"),
    ("flexibility", "Hip and ankle mobility"),
    ("general wellness", "Full-body strength"),
])
def test_starter_plan_schedule_matches_goal(goal, expected_day):
    plan=build_starter_plan(goal, "medium", 35)

    assert f"Goal: {goal.title()}" in plan
    assert expected_day in plan
    assert "Day 7 - Rest" in plan

def test_starter_plan_cardio_duration_does_not_apply_to_mobility():
    plan=build_starter_plan("muscle gain", "medium", 35)

    assert "Walk or cycle for 30 minutes at a conversational pace, then 5-10 minutes of gentle shoulder and hip mobility" in plan

@pytest.mark.parametrize("status_code", [429, 503])
def test_generation_uses_labeled_local_plan_when_gemini_is_unavailable(client, monkeypatch, status_code):
    def raise_overload(*args):
        raise gemini_client.errors.ServerError(status_code, {"error": {"code": status_code, "status": "UNAVAILABLE"}})

    monkeypatch.setattr("app.routes.generate_workout_gemini", raise_overload)
    response=client.post("/generate-workout", data={"name":"Morgan", "age":35, "weight":70, "goal":"muscle gain", "intensity":"medium"})

    assert response.status_code==200
    assert "local starter plan, not an AI-generated plan" in response.text
    assert "7-Day Starter Plan" in response.text
    assert "Day 7 - Rest" in response.text
    assert 'id="plan-text" lang="en-US"' in response.text

def test_generation_uses_local_plan_when_gemini_key_is_missing(client, monkeypatch):
    monkeypatch.setattr("app.routes.get_settings", lambda: SimpleNamespace(gemini_api_key=None))
    monkeypatch.setattr("app.routes.generate_workout_gemini", lambda *args: pytest.fail("Gemini should not be called"))
    response=client.post("/generate-workout", data={"name":"Morgan", "age":35, "weight":70, "goal":"flexibility", "intensity":"low"})

    assert response.status_code==200
    assert "Gemini is not configured" in response.text
    assert "Hip and ankle mobility" in response.text

@pytest.mark.parametrize(("module", "function", "args"), [
    (gemini_generator, gemini_generator.generate_workout_gemini, ("Alex", 30, 70, "general wellness", "medium", "es-ES")),
    (gemini_flash_generator, gemini_flash_generator.generate_nutrition_tip_with_flash, ("general wellness", 30, "fr-FR")),
    (updated_plan, updated_plan.update_workout_plan, ("Original plan", "make it lighter", 30, "general wellness", "medium", "hi-IN")),
])
def test_gemini_client_stays_open_during_request(monkeypatch, module, function, args):
    class FakeClient:
        is_open = False
        is_closed = False

        def __enter__(self):
            self.is_open = True
            return self

        def __exit__(self, *exc_info):
            self.is_open = False
            self.is_closed = True

        def generate_content(self, **kwargs):
            assert self.is_open
            self.request = kwargs
            return SimpleNamespace(text="Generated response")

        @property
        def models(self):
            return SimpleNamespace(generate_content=self.generate_content)

    client = FakeClient()
    monkeypatch.setattr(module, "get_settings", lambda: SimpleNamespace(
        gemini_api_key="test-key",
        gemini_workout_model="test-model",
        gemini_tip_model="test-model",
    ))
    monkeypatch.setattr(module.genai, "Client", lambda **kwargs: client)

    assert function(*args) == "Generated response"
    assert client.is_closed
    assert args[-1] in client.request["contents"]

def test_gemini_retry_recovers_from_temporary_503(monkeypatch):
    class Models:
        calls = 0

        def generate_content(self, **kwargs):
            self.calls += 1
            if self.calls < 3:
                raise gemini_client.errors.ServerError(503, {"error": {"code": 503, "status": "UNAVAILABLE"}})
            return "Generated response"

    models = Models()
    delays = []
    monkeypatch.setattr(gemini_client, "sleep", delays.append)

    response = gemini_client.generate_content_with_retry(SimpleNamespace(models=models), model="test-model")

    assert response == "Generated response"
    assert models.calls == 3
    assert delays == [1, 2]

def test_gemini_retry_stops_after_three_503_responses(monkeypatch):
    class Models:
        calls = 0
        models = []

        def generate_content(self, **kwargs):
            self.calls += 1
            self.models.append(kwargs["model"])
            raise gemini_client.errors.ServerError(503, {"error": {"code": 503, "status": "UNAVAILABLE"}})

    models = Models()
    delays = []
    monkeypatch.setattr(gemini_client, "sleep", delays.append)

    with pytest.raises(gemini_client.errors.ServerError):
        gemini_client.generate_content_with_retry(SimpleNamespace(models=models), model="test-model")

    assert models.calls == 5
    assert models.models == ["test-model", "test-model", "test-model", "gemini-3.7-flash", "gemini-3.6-flash"]
    assert delays == [1, 2]

def test_gemini_retry_uses_fallback_after_primary_503(monkeypatch):
    class Models:
        attempted = []

        def generate_content(self, **kwargs):
            self.attempted.append(kwargs["model"])
            if kwargs["model"] == "gemini-3.8-flash":
                raise gemini_client.errors.ServerError(503, {"error": {"code": 503, "status": "UNAVAILABLE"}})
            return "Fallback response"

    models = Models()
    delays = []
    monkeypatch.setattr(gemini_client, "sleep", delays.append)

    response = gemini_client.generate_content_with_retry(
        SimpleNamespace(models=models), model="gemini-3.8-flash", contents="test"
    )

    assert response == "Fallback response"
    assert models.attempted == ["gemini-3.8-flash"] * 3 + ["gemini-3.7-flash"]
    assert delays == [1, 2]

def test_gemini_quota_uses_fallback_immediately(monkeypatch):
    class Models:
        attempted = []

        def generate_content(self, **kwargs):
            self.attempted.append(kwargs["model"])
            if kwargs["model"] == "gemini-3.8-flash":
                raise gemini_client.errors.ServerError(429, {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED"}})
            return "Fallback response"

    models = Models()
    delays = []
    monkeypatch.setattr(gemini_client, "sleep", delays.append)

    response = gemini_client.generate_content_with_retry(
        SimpleNamespace(models=models), model="gemini-3.8-flash", contents="test"
    )

    assert response == "Fallback response"
    assert models.attempted == ["gemini-3.8-flash", "gemini-3.7-flash"]
    assert delays == []

def test_admin_requires_credentials(client):
    response=client.get("/view-all-users")
    assert response.status_code==401
    assert response.headers["www-authenticate"]=="Basic"

def test_admin_accepts_http_basic_auth(client):
    response=client.get("/view-all-users",auth=("admin","test-admin"))
    assert response.status_code==200

def test_admin_rejects_query_string_key(client):
    response=client.get("/view-all-users?key=test-admin")
    assert response.status_code==401

def test_admin_is_disabled_without_configured_key(client, monkeypatch):
    monkeypatch.setattr("app.dependencies.get_settings", lambda: SimpleNamespace(admin_key=None))
    response=client.get("/view-all-users",auth=("admin","test-admin"))
    assert response.status_code==503
