import uuid
import requests

BASE_URL = "http://127.0.0.1:5000"


def test_successful_registration():
    unique_suffix = uuid.uuid4().hex[:6]

    payload = {
        "username": f"autotest_{unique_suffix}",
        "password": "Password123"
    }

    response = requests.post(f"{BASE_URL}/register", json=payload)

    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"