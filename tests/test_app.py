import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def setup_function(function):
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_dict():
    # Arrange
    expected_activity = "Chess Club"

    with TestClient(app) as client:
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, dict)
        assert expected_activity in body
        assert body[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"
        assert isinstance(body[expected_activity]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    with TestClient(app) as client:
        # Act
        response = client.post(
            f"/activities/{encoded_activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
        assert email in activities[activity_name]["participants"]


def test_signup_duplicate_email_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    with TestClient(app) as client:
        # Act
        response = client.post(
            f"/activities/{encoded_activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    with TestClient(app) as client:
        # Act
        response = client.delete(
            f"/activities/{encoded_activity}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Removed {email} from {activity_name}"}
        assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_not_found():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    with TestClient(app) as client:
        # Act
        response = client.delete(
            f"/activities/{encoded_activity}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
