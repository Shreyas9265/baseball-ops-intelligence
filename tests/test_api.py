from __future__ import annotations

import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import server


class ApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        data_dir = Path(self.temp_dir.name) / "data"
        server.DATA_DIR = data_dir
        server.DB_PATH = data_dir / "test.db"
        server.initialize_database()

        self.httpd = ThreadingHTTPServer(("localhost", 0), server.BaseballOpsHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://localhost:{self.httpd.server_port}"

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.thread.join(timeout=2)
        self.httpd.server_close()
        self.temp_dir.cleanup()

    def get_json(self, path: str) -> dict:
        with urlopen(f"{self.base_url}{path}", timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def post_json(self, path: str, payload: dict) -> tuple[int, dict]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_health_endpoint(self) -> None:
        payload = self.get_json("/api/health")
        self.assertEqual(payload["status"], "ok")

    def test_players_endpoint_returns_seeded_players(self) -> None:
        payload = self.get_json("/api/players")
        self.assertEqual(len(payload["players"]), 5)
        self.assertEqual(payload["players"][0]["name"], "Mateo Alvarez")

    def test_recommendations_endpoint_returns_one_per_player(self) -> None:
        status, payload = self.post_json("/api/recommendations", {})
        self.assertEqual(status, 200)
        self.assertEqual(len(payload["recommendations"]), 5)
        self.assertIn("action", payload["recommendations"][0])

    def test_workflow_creation(self) -> None:
        status, payload = self.post_json(
            "/api/workflows",
            {
                "playerId": 1,
                "title": "Review defensive alignment package",
                "owner": "Analytics",
                "priority": "Medium",
                "dueDate": "2026-06-20",
            },
        )

        self.assertEqual(status, 201)
        self.assertEqual(payload["status"], "created")

        workflows = self.get_json("/api/workflows")["workflows"]
        self.assertTrue(any(task["title"] == "Review defensive alignment package" for task in workflows))

    def test_workflow_creation_rejects_unknown_player(self) -> None:
        request = Request(
            f"{self.base_url}/api/workflows",
            data=json.dumps(
                {
                    "playerId": 999,
                    "title": "Invalid task",
                    "owner": "Analytics",
                    "priority": "Medium",
                    "dueDate": "2026-06-20",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.assertRaises(HTTPError) as error:
            urlopen(request, timeout=5)

        self.assertEqual(error.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
