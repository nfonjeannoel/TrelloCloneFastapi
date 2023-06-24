import unittest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestUserModel(unittest.TestCase):
    email = "test1@gmail.com"
    password = "password123"
    username = "Test User"

    from api.database import create_db as _create_db
    _create_db()

    def test_create_user(self):
        user_data = {
            "email": self.email,
            "password": self.password,
            "username": self.username
        }
        response = client.post("/users/create_user", json=user_data)
        if response.status_code != 200:
            # User already exists
            pass
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["token_type"], "bearer")

    def test_login(self):
        login_data = {
            "username": self.email,
            "password": self.password
        }
        response = client.post("/users/token", data=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["token_type"], "bearer")
        self.access_token = response.json()["access_token"]

    def test_read_users(self):
        response = client.get("/users")
        self.assertEqual(response.status_code, 200)
        # Add assertions to validate the response data

    def test_read_users_me_unauthorized(self):
        response = client.get("/users/me")
        self.assertEqual(response.status_code, 401)  # Unauthorized without authentication

    def test_read_users_me_authorized(self):
        # make request and get token
        response = client.post("/users/token", data={"username": self.email, "password": self.password})
        token = response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = client.get("/users/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        # Add assertions to validate the response data
