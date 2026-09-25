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

## Run Locally

1. Install Python 3.10 or newer and MySQL, then create an empty database for the application.
2. Create and activate a virtual environment from the repository root:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` and configure the MySQL connection and JWT signing key:

   ```dotenv
   DATABASE_URL=mysql+pymysql://root:your-password@localhost/library_db
   JWT_SECRET_KEY=replace-with-a-long-random-value
   ```

5. Apply the database migrations:

   ```bash
   flask --app app db upgrade
   ```

6. Start Flask on the port expected by the React client:

   ```bash
   flask --app app run --debug --port 5000
   ```

7. Verify the API at `http://localhost:5000/test_db`, then start the `Biblio_React` frontend in another terminal.
