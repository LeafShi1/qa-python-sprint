import os, requests
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.example.com")
TOKEN = os.getenv("API_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

def test_get_user_200():
    r = requests.get(f"{BASE_URL}/users/123", headers=HEADERS, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 123
    assert "name" in data
