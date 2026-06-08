# Baseball Ops Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

A GitHub-ready full-stack baseball operations project that integrates player data collection, analytics reporting, workflow management, and AI-style recommendations into one decision-support platform.

This project was built to match a Full Stack Engineer role focused on complex applications, frontend/backend development, API integrations, database architecture, cloud readiness, product improvement, stakeholder collaboration, and baseball operations tooling.

## Demo

Run locally and open:

```text
http://localhost:8000
```

The app includes seeded sample data for players, metrics, scouting reports, and baseball operations workflow tasks.

## Features

- Player roster dashboard with readiness, workload, performance, and scouting context
- REST API for players, reports, workflow tasks, health checks, and recommendations
- SQLite database with normalized player, metric, report, and workflow tables
- AI-style recommendation engine for promotion readiness, workload review, rehab tracking, and tactical usage
- Workflow creation form for cross-functional baseball operations follow-up tasks
- Responsive frontend built with HTML, CSS, and JavaScript
- Docker and Docker Compose support
- GitHub Actions CI with Python 3.10, 3.11, and 3.12 test coverage
- No third-party runtime dependencies

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | HTML, CSS, JavaScript |
| Backend | Python standard library HTTP server |
| Database | SQLite |
| Testing | Python `unittest` |
| CI | GitHub Actions |
| Deployment | Docker-ready |

## Role Requirements Mapping

| Requirement | Project Evidence |
| --- | --- |
| Full stack engineering | Browser dashboard, REST API, SQLite persistence, backend routing |
| Frontend and backend development | Interactive UI consumes backend JSON endpoints |
| API integrations | `/api/*` endpoints connect roster, reports, workflows, and recommendations |
| Database architecture | Normalized tables with foreign keys and seeded domain data |
| Cloud infrastructure | `Dockerfile`, `docker-compose.yml`, environment-based host/port config |
| Product functionality | Analytics summaries, workflow tracking, recommendations, reports |
| Stakeholder collaboration | Tools designed for baseball ops, scouting, medical, analytics, and player development groups |

## Getting Started

### Prerequisites

- Python 3.10+
- Optional: Docker

### Local Development

```bash
git clone https://github.com/YOUR_USERNAME/baseball-ops-intelligence.git
cd baseball-ops-intelligence
python server.py
```

Open:

```text
http://localhost:8000
```

The database is created automatically at:

```text
data/baseball_ops.db
```

### Environment Variables

Copy `.env.example` if you want to document local values:

```bash
HOST=localhost
PORT=8000
```

For Docker or cloud hosting, use:

```bash
HOST=0.0.0.0
PORT=8000
```

## Docker

Build and run:

```bash
docker build -t baseball-ops-intelligence .
docker run -p 8000:8000 baseball-ops-intelligence
```

Or use Compose:

```bash
docker compose up --build
```

## Testing

```bash
python -m unittest discover -s tests
```

The tests spin up a temporary API server, create an isolated SQLite database, and validate core endpoints.

## API Reference

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | Service health check |
| GET | `/api/players` | Latest player metrics and roster context |
| GET | `/api/players/{id}` | Player profile, metric history, and reports |
| GET | `/api/reports` | Baseball operations reports |
| GET | `/api/workflows` | Workflow task queue |
| POST | `/api/workflows` | Create a new workflow task |
| POST | `/api/recommendations` | Generate AI-style recommendations |

Example workflow payload:

```json
{
  "playerId": 1,
  "title": "Review defensive alignment package",
  "owner": "Analytics",
  "priority": "Medium",
  "dueDate": "2026-06-20"
}
```

## Project Structure

```text
baseball-ops-intelligence/
  .github/workflows/ci.yml
  static/
    app.js
    index.html
    styles.css
  tests/
    test_api.py
  .env.example
  .gitignore
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  README.md
  SECURITY.md
  docker-compose.yml
  pyproject.toml
  requirements.txt
  server.py
```

## Future Improvements

- Add authentication and role-based access control
- Replace seeded data with ingestion from tracking, scouting, or warehouse systems
- Add real model-backed recommendations through an AI service integration
- Add audit logs for workflow changes
- Add charts for metric history and team-level trends
- Add PostgreSQL support for production deployments

## Portfolio Summary

> Baseball Ops Intelligence is a full-stack decision-support platform for baseball operations teams. It combines player data collection, analytics reporting, AI-assisted recommendations, and workflow management so stakeholders can make faster, more consistent player development and roster decisions.

