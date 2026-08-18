# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Persist activities and registrations across server restarts

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application from the repository root:

   ```
   uvicorn src.app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                      |

## Database

The application initializes `src/activities.db` automatically on first start.
Activities from `src/activities.json` are imported only when the database has
no activities, so the JSON file remains seed data rather than a second source
of truth. Registrations made through the API are stored in SQLite and survive
application restarts.

Set `MERGINGTON_DB_PATH` to use a different database location:

```
MERGINGTON_DB_PATH=/path/to/activities.db uvicorn src.app:app --reload
```

For a fresh local database, stop the application and delete the `.db` file;
the next start recreates the schema and imports the seed data. A future move to
a larger database should introduce versioned schema migrations and import the
SQLite records, while preserving the repository interface used by the API.

Run the isolated test suite with:

```
python -m unittest discover -s tests -v
```

## Data Model

The application uses separate SQLite records with stable integer identifiers:

1. **Activities**

   - ID
   - Name
   - Description
   - Schedule
   - Maximum number of participants allowed

2. **Registrations**
   - ID
   - Activity ID
   - Student email

The database enforces one registration per student email and activity.
