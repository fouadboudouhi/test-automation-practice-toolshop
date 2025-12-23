import uuid
import requests

def test_healthcheck(base_url):
    r = requests.get(f"{base_url}/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_create_and_get_user(base_url):
    payload = {"email": "a@example.com", "name": "Alice", "is_active": True}
    r = requests.post(f"{base_url}/api/users", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == payload["email"]
    assert body["name"] == payload["name"]
    user_id = body["id"]

    r2 = requests.get(f"{base_url}/api/users/{user_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == user_id

def test_duplicate_email_returns_409(base_url):
    payload = {"email": "dup@example.com", "name": "A", "is_active": True}
    assert requests.post(f"{base_url}/api/users", json=payload).status_code == 201
    r2 = requests.post(f"{base_url}/api/users", json=payload)
    assert r2.status_code == 409
    assert r2.json()["detail"]

def test_not_found_returns_404(base_url):
    missing = str(uuid.uuid4())
    r = requests.get(f"{base_url}/api/users/{missing}")
    assert r.status_code == 404

def test_invalid_payload_returns_422(base_url):
    payload = {"email": "not-an-email", "name": ""}
    r = requests.post(f"{base_url}/api/users", json=payload)
    assert r.status_code == 422

def test_update_user(base_url):
    payload = {"email": "u@example.com", "name": "User", "is_active": True}
    r = requests.post(f"{base_url}/api/users", json=payload)
    user_id = r.json()["id"]

    upd = {"name": "User Updated"}
    r2 = requests.put(f"{base_url}/api/users/{user_id}", json=upd)
    assert r2.status_code == 200
    assert r2.json()["name"] == "User Updated"

def test_delete_user(base_url):
    payload = {"email": "d@example.com", "name": "Del", "is_active": True}
    r = requests.post(f"{base_url}/api/users", json=payload)
    user_id = r.json()["id"]

    r2 = requests.delete(f"{base_url}/api/users/{user_id}")
    assert r2.status_code == 204

    r3 = requests.get(f"{base_url}/api/users/{user_id}")
    assert r3.status_code == 404
