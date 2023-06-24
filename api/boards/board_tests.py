import unittest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestTodoModel(unittest.TestCase):
    email = "test3@gmail.com"
    password = "password123"
    username = "Test User"

    from api.database import create_db as _create_db
    _create_db()

    def setUp(self):
        self.create_user()
        self.access_token = self.login_and_get_token()

    def create_user(self):
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

    def login_and_get_token(self):
        login_data = {
            "username": self.email,
            "password": self.password
        }
        response = client.post("/users/token", data=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["token_type"], "bearer")
        return response.json()["access_token"]

    def test_create_board_unauthorized(self):
        board_data = {
            "name": "Board name 2",
            "is_public": True
        }
        response = client.post("/boards/create_board", json=board_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Not authenticated")

    def test_create_board_authorized(self):
        board_data = {
            "name": "Board name 2",
            "is_public": True
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = client.post("/boards/create_board", json=board_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], board_data["name"])

    def test_read_boards_by_user_unauthorized(self):
        response = client.get("/boards")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Not authenticated")

    def test_read_boards_by_user_authorized(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = client.get("/boards", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.json(), list), True)

    def test_read_user_board_by_id_unauthorized(self):
        response = client.get("/boards/1")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Not authenticated")

    def create_board_and_get_id(self):
        # Create a board and get its id
        board_data = {
            "name": "Board name 2",
            "is_public": True
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        response = client.post("/boards/create_board", json=board_data, headers=headers)
        return response.json(), board_data

    def test_read_user_board_by_id_authorized(self):
        board, old_board = self.create_board_and_get_id()
        board_id = board["id"]
        board_data = old_board
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = client.get(f"/boards/{board_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], board_data["name"])
        self.assertEqual(response.json()["id"], board_id)

    def test_update_user_board_by_id_unauthorized(self):
        response = client.put("/boards/1")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Not authenticated")

    def test_update_user_board_by_id_authorized(self):
        board, old_board = self.create_board_and_get_id()
        board_id = board["id"]
        board_data = old_board
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        board_data["name"] = "New board name"
        response = client.put(f"/boards/{board_id}", json=board_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], board_data["name"])
        self.assertEqual(response.json()["id"], board_id)

    def test_delete_user_board_by_id_unauthorized(self):
        board, old_board = self.create_board_and_get_id()
        board_id = board["id"]
        response = client.delete(f"/boards/{board_id}")
        self.assertEqual(response.status_code, 401)

    def test_delete_user_board_by_id_unauthorized(self):
        board, old_board = self.create_board_and_get_id()
        board_id = board["id"]
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = client.delete(f"/boards/{board_id}", headers=headers)
        self.assertEqual(response.status_code, 204)
