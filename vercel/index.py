"""Vercel serverless entry point for Baseball Ops Intelligence (standard library only)."""
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _server as server  # noqa: E402

# Only /tmp is writable on Vercel; the database is re-seeded on each cold start.
server.DATA_DIR = Path("/tmp/baseball-ops")
server.DB_PATH = server.DATA_DIR / "baseball_ops.db"
server.initialize_database()


class handler(server.BaseballOpsHandler):
    """The rewrite sends /api/<route> here as ?__route=<route>; restore the original path, then run the app's handler."""

    def _restore_path(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qsl(parsed.query, keep_blank_values=True)
        route = next((v for k, v in params if k == "__route"), None)
        if route is not None:
            rest = urlencode([(k, v) for k, v in params if k != "__route"])
            self.path = "/api/" + route.lstrip("/") + (f"?{rest}" if rest else "")

    def do_GET(self) -> None:
        self._restore_path()
        super().do_GET()

    def do_POST(self) -> None:
        self._restore_path()
        super().do_POST()
