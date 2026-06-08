# Contributing

Thanks for improving Baseball Ops Intelligence.

## Local Setup

```bash
python server.py
```

Run tests before opening a pull request:

```bash
python -m unittest discover -s tests
```

## Pull Request Checklist

- Keep changes focused on one feature or fix.
- Add or update tests when API behavior changes.
- Update `README.md` when setup, endpoints, or user-facing behavior changes.
- Avoid committing generated SQLite databases from `data/`.

