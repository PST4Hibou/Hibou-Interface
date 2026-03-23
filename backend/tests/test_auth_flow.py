import os
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from config import get_settings
from main import create_app


class AuthFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(cls.temp_dir.name) / "test_auth.db"
        cls.env_backup = {
            "DATABASE_URL": os.environ.get("DATABASE_URL"),
            "JWT_SECRET": os.environ.get("JWT_SECRET"),
            "FRONTEND_ORIGINS": os.environ.get("FRONTEND_ORIGINS"),
            "ZMQ_PUB_BIND": os.environ.get("ZMQ_PUB_BIND"),
        }

        os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
        os.environ["JWT_SECRET"] = "integration-test-secret"
        os.environ["FRONTEND_ORIGINS"] = "http://localhost:3000"
        os.environ["ZMQ_PUB_BIND"] = "inproc://auth-tests"

        get_settings.cache_clear()
        cls.client_context = TestClient(create_app())
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_context.__exit__(None, None, None)
        cls.temp_dir.cleanup()

        for key, value in cls.env_backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        get_settings.cache_clear()

    def test_register_login_and_me(self) -> None:
        identifier = f"user-{uuid4().hex[:8]}"
        password = "a-strong-password"
        payload = {"identifier": identifier, "password": password}

        register_response = self.client.post("/auth/register", json=payload)
        self.assertEqual(register_response.status_code, 201)
        register_body = register_response.json()
        self.assertEqual(register_body["identifier"], identifier)
        self.assertIn("id", register_body)
        self.assertNotIn("hashed_password", register_body)

        duplicate_register = self.client.post("/auth/register", json=payload)
        self.assertEqual(duplicate_register.status_code, 409)

        login_response = self.client.post("/auth/login", json=payload)
        self.assertEqual(login_response.status_code, 200)
        login_body = login_response.json()
        self.assertEqual(login_body["token_type"], "bearer")
        self.assertIn("access_token", login_body)
        self.assertEqual(login_body["user"]["identifier"], identifier)

        me_response = self.client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {login_body['access_token']}"},
        )
        self.assertEqual(me_response.status_code, 200)
        me_body = me_response.json()
        self.assertEqual(me_body["identifier"], identifier)
        self.assertEqual(me_body["id"], register_body["id"])

    def test_rejects_invalid_credentials(self) -> None:
        identifier = f"user-{uuid4().hex[:8]}"
        payload = {"identifier": identifier, "password": "a-strong-password"}

        register_response = self.client.post("/auth/register", json=payload)
        self.assertEqual(register_response.status_code, 201)

        invalid_login = self.client.post(
            "/auth/login",
            json={"identifier": identifier, "password": "wrong-password"},
        )
        self.assertEqual(invalid_login.status_code, 401)

    def test_me_requires_bearer_token(self) -> None:
        me_response = self.client.get("/auth/me")
        self.assertEqual(me_response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
