import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

initial_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))

client = TestClient(app)

def test_get_activities_returns_all_activities():
    # Arrange
    # (initial data already provided by fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity_success():
    # Arrange
    email = "student-aaa@example.com"
    activity = "Chess Club"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert email in activities[activity]["participants"]


def test_signup_duplicate_fails_with_400():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    assert email in activities[activity]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_remove_participant_success():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    assert email in activities[activity]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found():
    # Arrange
    email = "nobody@mergington.edu"
    activity = "Chess Club"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_signup_nonexistent_activity_fails_with_404():
    # Arrange
    activity = "Nonexistent Club"

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": "extra@mergington.edu"}
    )

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_from_nonexistent_activity_fails_with_404():
    # Arrange
    activity = "Nonexistent Club"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants", params={"email": "extra@mergington.edu"}
    )

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
