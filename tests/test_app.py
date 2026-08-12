from copy import deepcopy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_get_activities_returns_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()


def test_signup_adds_participant():
    activity = quote("Chess Club", safe="")
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity}/signup?email={quote(email, safe='')}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    activity = quote("Chess Club", safe="")
    email = "repeat@mergington.edu"

    first = client.post(f"/activities/{activity}/signup?email={quote(email, safe='')}")
    assert first.status_code == 200

    second = client.post(f"/activities/{activity}/signup?email={quote(email, safe='')}")
    assert second.status_code == 400
    assert second.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404():
    activity = quote("Nonexistent Club", safe="")
    email = "student@mergington.edu"

    response = client.post(f"/activities/{activity}/signup?email={quote(email, safe='')}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant():
    activity = quote("Programming Class", safe="")
    email = "emma@mergington.edu"

    response = client.delete(f"/activities/{activity}/participants?email={quote(email, safe='')}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Programming Class"
    assert email not in activities["Programming Class"]["participants"]


def test_remove_nonexistent_participant_returns_400():
    activity = quote("Programming Class", safe="")
    email = "missing@mergington.edu"

    response = client.delete(f"/activities/{activity}/participants?email={quote(email, safe='')}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_remove_nonexistent_activity_returns_404():
    activity = quote("Unknown Club", safe="")
    email = "student@mergington.edu"

    response = client.delete(f"/activities/{activity}/participants?email={quote(email, safe='')}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
