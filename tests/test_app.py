import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_activities_returns_activity_catalog(client):
    response = client.get('/activities')

    assert response.status_code == 200
    body = response.json()
    assert 'Chess Club' in body
    assert body['Chess Club']['max_participants'] == 12


def test_signup_for_activity_adds_participant(client):
    response = client.post(
        '/activities/Chess Club/signup',
        params={'email': 'newstudent@mergington.edu'},
    )

    assert response.status_code == 200
    assert response.json()['message'] == 'Signed up newstudent@mergington.edu for Chess Club'
    assert 'newstudent@mergington.edu' in activities['Chess Club']['participants']


def test_duplicate_signup_returns_400(client):
    response = client.post(
        '/activities/Chess Club/signup',
        params={'email': 'michael@mergington.edu'},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'Student is already signed up for this activity'


def test_remove_participant_removes_existing_student(client):
    response = client.delete(
        '/activities/Chess Club/participant',
        params={'email': 'michael@mergington.edu'},
    )

    assert response.status_code == 200
    assert 'michael@mergington.edu' not in activities['Chess Club']['participants']


def test_signup_for_unknown_activity_returns_404(client):
    response = client.post(
        '/activities/Unknown Club/signup',
        params={'email': 'student@mergington.edu'},
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'Activity not found'
