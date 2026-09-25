# Biblio Flask API

REST API for a library management system. It manages books, authors, members, classes, borrowing records, authentication, and dashboard data for the companion React application.

## Tech Stack

- Python and Flask
- SQLAlchemy and Flask-Migrate
- Marshmallow schemas
- JWT authentication
- Docker support

## Project Structure

```text
models/       Database models
resources/    API controllers and resources
migrations/   Alembic database migrations
app.py        Flask application entry point
db.py         Database initialization
schemas.py    Serialization schemas
```

## Getting Started

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
flask db upgrade
flask run
```

Configure the database URL and authentication secrets in local environment variables before starting the API. The frontend lives in the `Biblio_React` repository.
