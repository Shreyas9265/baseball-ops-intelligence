from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "baseball_ops.db"


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with closing(connect()) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                level TEXT NOT NULL,
                bats TEXT NOT NULL,
                throws TEXT NOT NULL,
                age INTEGER NOT NULL,
                org_rank INTEGER NOT NULL,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS player_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                collected_at TEXT NOT NULL,
                ops REAL NOT NULL,
                woba REAL NOT NULL,
                sprint_speed REAL NOT NULL,
                throwing_velocity REAL NOT NULL,
                workload_index INTEGER NOT NULL,
                readiness_score INTEGER NOT NULL,
                FOREIGN KEY(player_id) REFERENCES players(id)
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                author TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(player_id) REFERENCES players(id)
            );

            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                owner TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                due_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(player_id) REFERENCES players(id)
            );
            """
        )

        player_count = db.execute("SELECT COUNT(*) AS count FROM players").fetchone()["count"]
        if player_count:
            db.commit()
            return

        players = [
            ("Mateo Alvarez", "SS", "AAA", "R", "R", 23, 2, "Active"),
            ("Caleb Rios", "RHP", "AA", "L", "R", 22, 5, "Pitch build-up"),
            ("Jonah Price", "CF", "High-A", "L", "L", 21, 8, "Active"),
            ("Evan Brooks", "C", "AA", "R", "R", 24, 11, "Rehab assignment"),
            ("Nico Bennett", "1B", "AAA", "L", "L", 25, 14, "Active"),
        ]
        db.executemany(
            """
            INSERT INTO players (name, position, level, bats, throws, age, org_rank, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            players,
        )

        metrics = [
            (1, "2026-05-25T14:30:00Z", .884, .378, 28.7, 88.2, 62, 91),
            (1, "2026-06-02T14:30:00Z", .921, .396, 28.9, 88.6, 66, 94),
            (2, "2026-05-24T18:15:00Z", .000, .000, 25.1, 96.4, 74, 82),
            (2, "2026-06-01T18:15:00Z", .000, .000, 25.3, 97.1, 78, 84),
            (3, "2026-05-26T13:10:00Z", .762, .336, 30.1, 84.5, 54, 88),
            (3, "2026-06-03T13:10:00Z", .801, .352, 30.4, 85.0, 58, 90),
            (4, "2026-05-26T16:00:00Z", .691, .309, 24.6, 79.2, 43, 72),
            (4, "2026-06-03T16:00:00Z", .718, .318, 24.9, 80.5, 47, 76),
            (5, "2026-05-27T19:30:00Z", .846, .361, 25.8, 81.1, 69, 86),
            (5, "2026-06-04T19:30:00Z", .873, .372, 26.0, 81.6, 72, 87),
        ]
        db.executemany(
            """
            INSERT INTO player_metrics
                (player_id, collected_at, ops, woba, sprint_speed, throwing_velocity, workload_index, readiness_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            metrics,
        )

        reports = [
            (1, "Call-up readiness review", "Plate discipline and defensive actions both trend toward major-league readiness.", "Pro Scouting", "2026-06-04T12:00:00Z"),
            (2, "Pitch design checkpoint", "Four-seam velocity is up while workload is approaching the upper bound for this build phase.", "Player Development", "2026-06-03T12:00:00Z"),
            (3, "Range and baserunning review", "Elite sprint metrics support aggressive outfield positioning and late-game running usage.", "Baseball Analytics", "2026-06-05T12:00:00Z"),
            (4, "Rehab receiving report", "Receiving workload can increase gradually; throwing progression needs another review.", "Medical Ops", "2026-06-05T15:00:00Z"),
            (5, "Power consistency memo", "Contact quality remains strong, but workload should be monitored across the next series.", "Hitting Group", "2026-06-06T10:00:00Z"),
        ]
        db.executemany(
            """
            INSERT INTO reports (player_id, title, summary, author, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            reports,
        )

        workflows = [
            (1, "Finalize MLB bench fit summary", "Baseball Ops", "In Review", "High", "2026-06-12", "2026-06-04T16:00:00Z"),
            (2, "Review next bullpen pitch mix", "Pitching Dev", "Open", "Medium", "2026-06-10", "2026-06-03T16:00:00Z"),
            (4, "Confirm throwing progression", "Medical Ops", "Open", "High", "2026-06-09", "2026-06-05T16:00:00Z"),
            (5, "Add series workload note", "Analytics", "Done", "Low", "2026-06-08", "2026-06-02T16:00:00Z"),
        ]
        db.executemany(
            """
            INSERT INTO workflows (player_id, title, owner, status, priority, due_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            workflows,
        )
        db.commit()


def latest_player_rows() -> list[sqlite3.Row]:
    with closing(connect()) as db:
        return db.execute(
            """
            SELECT
                p.*,
                m.ops,
                m.woba,
                m.sprint_speed,
                m.throwing_velocity,
                m.workload_index,
                m.readiness_score,
                m.collected_at
            FROM players p
            JOIN player_metrics m ON m.player_id = p.id
            WHERE m.collected_at = (
                SELECT MAX(collected_at)
                FROM player_metrics
                WHERE player_id = p.id
            )
            ORDER BY p.org_rank ASC
            """
        ).fetchall()


def row_to_dict(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


def build_recommendation(player: dict) -> dict:
    if player["readiness_score"] >= 92:
        action = "Prioritize for MLB readiness meeting"
        rationale = "Readiness and offensive indicators are both above internal promotion thresholds."
    elif player["workload_index"] >= 75:
        action = "Schedule workload review before next appearance"
        rationale = "Recent workload is elevated enough to require cross-functional review."
    elif player["status"].lower().startswith("rehab"):
        action = "Keep rehab workflow active"
        rationale = "Rehab status and throwing metrics suggest a gradual progression plan."
    elif player["sprint_speed"] >= 30:
        action = "Surface for defensive positioning and baserunning package"
        rationale = "Speed metrics create immediate tactical value for game-planning."
    else:
        action = "Maintain current development plan"
        rationale = "Performance is stable with no urgent intervention detected."

    return {
        "playerId": player["id"],
        "player": player["name"],
        "action": action,
        "rationale": rationale,
        "confidence": min(96, max(72, int(player["readiness_score"] * 0.75 + (100 - player["workload_index"]) * 0.2))),
    }


class BaseballOpsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self.send_json({"status": "ok", "service": "baseball-ops-intelligence"})
            return
        if parsed.path == "/api/players":
            players = [row_to_dict(row) for row in latest_player_rows()]
            self.send_json({"players": players})
            return
        if parsed.path.startswith("/api/players/"):
            self.send_player(parsed.path)
            return
        if parsed.path == "/api/reports":
            self.send_reports()
            return
        if parsed.path == "/api/workflows":
            self.send_workflows()
            return

        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/recommendations":
            players = [row_to_dict(row) for row in latest_player_rows()]
            self.send_json({"recommendations": [build_recommendation(player) for player in players]})
            return
        if parsed.path == "/api/workflows":
            self.create_workflow()
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    def read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_player(self, path: str) -> None:
        try:
            player_id = int(path.rsplit("/", 1)[1])
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid player id")
            return

        with closing(connect()) as db:
            player = db.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
            metrics = db.execute(
                "SELECT * FROM player_metrics WHERE player_id = ? ORDER BY collected_at DESC",
                (player_id,),
            ).fetchall()
            reports = db.execute(
                "SELECT * FROM reports WHERE player_id = ? ORDER BY created_at DESC",
                (player_id,),
            ).fetchall()

        if not player:
            self.send_error(HTTPStatus.NOT_FOUND, "Player not found")
            return

        self.send_json(
            {
                "player": row_to_dict(player),
                "metrics": [row_to_dict(row) for row in metrics],
                "reports": [row_to_dict(row) for row in reports],
            }
        )

    def send_reports(self) -> None:
        with closing(connect()) as db:
            rows = db.execute(
                """
                SELECT reports.*, players.name AS player
                FROM reports
                JOIN players ON players.id = reports.player_id
                ORDER BY reports.created_at DESC
                """
            ).fetchall()
        self.send_json({"reports": [row_to_dict(row) for row in rows]})

    def send_workflows(self) -> None:
        with closing(connect()) as db:
            rows = db.execute(
                """
                SELECT workflows.*, players.name AS player
                FROM workflows
                JOIN players ON players.id = workflows.player_id
                ORDER BY
                    CASE workflows.status
                        WHEN 'Open' THEN 1
                        WHEN 'In Review' THEN 2
                        ELSE 3
                    END,
                    workflows.due_date ASC
                """
            ).fetchall()
        self.send_json({"workflows": [row_to_dict(row) for row in rows]})

    def create_workflow(self) -> None:
        try:
            payload = self.read_json_body()
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON")
            return

        required = ["playerId", "title", "owner", "priority", "dueDate"]
        missing = [field for field in required if not payload.get(field)]
        if missing:
            self.send_json({"error": f"Missing fields: {', '.join(missing)}"}, HTTPStatus.BAD_REQUEST)
            return

        if payload["priority"] not in {"High", "Medium", "Low"}:
            self.send_json({"error": "Priority must be High, Medium, or Low"}, HTTPStatus.BAD_REQUEST)
            return

        with closing(connect()) as db:
            player = db.execute("SELECT id FROM players WHERE id = ?", (int(payload["playerId"]),)).fetchone()
            if not player:
                self.send_json({"error": "Player not found"}, HTTPStatus.NOT_FOUND)
                return

            db.execute(
                """
                INSERT INTO workflows (player_id, title, owner, status, priority, due_date, created_at)
                VALUES (?, ?, ?, 'Open', ?, ?, ?)
                """,
                (
                    int(payload["playerId"]),
                    payload["title"].strip(),
                    payload["owner"].strip(),
                    payload["priority"],
                    payload["dueDate"],
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            db.commit()

        self.send_json({"status": "created"}, HTTPStatus.CREATED)


def main() -> None:
    initialize_database()
    host = os.environ.get("HOST", "localhost")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), BaseballOpsHandler)
    print(f"Baseball Ops Intelligence running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
