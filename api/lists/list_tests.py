import unittest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestList(unittest.TestCase):
    email = "test3@gmail.com"
    password = "password123"
    username = "Test User"

    from api.database import create_db as _create_db
    _create_db()

    def setUp(self):
        self.create_user()
        self.access_token = self.login_and_get_token()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        self.board = self.create_board()
        self.list = self.create_list()

    def create_board(self):
        response = client.post("/boards/create_board", json={
            "name": "Board name 2",
            "is_public": True
        }, headers=self.headers)
        return response.json()

    def create_list(self):
        response = client.post(f"/lists/{self.board['id']}/create_list", json={
            "name": "List name",
            "position": 0
        }, headers=self.headers)
        return response.json()

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

    def test_create_list(self):
        response = client.post(f"/lists/{self.board['id']}/create_list", json={
            "name": "List name",
            "position": 0
        }, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        list_data = response.json()
        self.assertIn("id", list_data)
        self.assertEqual(list_data["name"], "List name")
        self.assertEqual(list_data["board_id"], self.board["id"])

    def test_create_list_unauthorized(self):
        response = client.post(f"/lists/{self.board['id']}/create_list", json={
            "name": "List name",
            "position": 0
        })
        self.assertEqual(response.status_code, 401)

    def test_get_board_lists(self):
        response = client.get(f"/lists/{self.board['id']}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        lists = response.json()
        self.assertEqual(isinstance(lists, list), True)

        list_data = lists[0]
        self.assertEqual(list_data['board_id'], self.board['id'])

    def test_get_board_lists_unauthorized(self):
        response = client.get(f"/lists/{self.board['id']}")
        self.assertEqual(response.status_code, 401)

    def test_get_board_list(self):
        list_id = self.list["id"]
        response = client.get(f"/lists/{list_id}/{self.board['id']}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        list_data = response.json()
        self.assertEqual(list_data["id"], list_id)
        self.assertEqual(list_data["board_id"], self.board["id"])

    def test_update_board_list(self):
        list_id = self.list["id"]
        response = client.put(f"/lists/{list_id}/{self.board['id']}", json={
            "name": "Updated List",
            "position": 1
        }, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        list_data = response.json()
        self.assertEqual(list_data["id"], list_id)
        self.assertEqual(list_data["name"], "Updated List")
        self.assertEqual(list_data["position"], 1)

    def test_delete_board_list(self):
        list_id = self.list["id"]
        response = client.delete(f"/lists/{list_id}/{self.board['id']}", headers=self.headers)
        self.assertEqual(response.status_code, 204)
        # Verify the list is deleted
        response = client.get(f"/lists/{list_id}/{self.board['id']}", headers=self.headers)
        self.assertEqual(response.status_code, 404)
