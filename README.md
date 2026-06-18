# DevTrack

DevTrack is a small backend API for tracking engineering issues. Engineers can create issues, set priorities, update status, and register reporters. Data is persisted to local JSON files (no external database required by default).

**Key features**
- Create and list issues with priorities and status
- Register reporters (name, email, optional team)
- Simple JSON file storage for easy inspection and portability

**Status:** Prototype / Educational

**Contents**
- **Project description** — what this service does
- **API endpoints** — how to interact with the service
- **Setup** — how to run locally
- **Examples** — sample requests/responses and screenshot placeholders

**Project structure**
- `manage.py` and Django project files under this folder
- `issues/` — application implementing the Issue and Reporter API
- `issues.json` and `reporters.json` — default JSON data files (created automatically or can be seeded)

---

**API Endpoints**

**Reporter Endpoints**

| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/reporters/ | Create a new reporter |
| GET | /api/reporters/ | Get all reporters |
| GET | /api/reporters/?id=1 | Get reporter by ID |

**Issue Endpoints**

| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/issues/ | Create a new issue |
| GET | /api/issues/ | Get all issues |
| GET | /api/issues/?id=1 | Get issue by ID |
| GET | /api/issues/?status=open | Filter issues by status |

---

Base path: `/api`

1) List / create issues
- `GET /api/issues/` — returns all issues. Optional query params:

Example:

```
curl -s "http://127.0.0.1:8000/api/issues/"
```

- `POST /api/issues/` — create a new issue. JSON body fields:
	- `title` (string, required)
	- `description` (string, optional)
	- `reporter_id` (integer, required)
	- `status` (optional, defaults to `open`) — one of `open`, `in_progress`, `closed`
	- `priority` (optional, defaults to `medium`) — one of `low`, `medium`, `high`, `critical`

Example request:

```
curl -X POST http://127.0.0.1:8000/api/issues/ \
	-H "Content-Type: application/json" \
	-d '{"title":"Fix login bug","description":"Users cannot login","reporter_id":1,"priority":"high"}'
```

Example success response (201):

```
{
	"success": true,
	"data": {
		"id": 3,
		"title": "Fix login bug",
		"description": "Users cannot login",
		"status": "open",
		"priority": "high",
		"reporter_id": 1,
		"message": "<human readable description from model>"
	},
	"error": null
}
```

2) List / create reporters
- `GET /api/reporters/` — returns all reporters. Optional query param `id` to fetch single reporter.
- `POST /api/reporters/` — create reporter. JSON body fields:
	- `name` (string, required)
	- `email` (string, required, must contain `@`)
	- `team` (string, optional)

Example request:

```
curl -X POST http://127.0.0.1:8000/api/reporters/ \
	-H "Content-Type: application/json" \
	-d '{"name":"Alice","email":"alice@example.com","team":"backend"}'
```

Example response (201):

```
{
	"success": true,
	"data": {
		"id": 2,
		"name": "Alice",
		"email": "alice@example.com",
		"team": "backend"
	},
	"error": null
}
```

---

**Setup (local)**

Prerequisites
- Python 3.10+ (3.11 recommended)
- pip

Steps

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. (Optional) Configure environment

If you want to override the data file names, create a `.env` file in the project root with:

```
ISSUES_FILE_NAME=issues.json
REPORTERS_FILE_NAME=reporters.json
```

4. Ensure data files exist (optional — the app handles missing files but you can create empty lists to start)

```bash
echo '[]' > issues.json
echo '[]' > reporters.json
```

5. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

---

**Examples & Screenshots**
Below are example request/response screenshots included in this repository. The images are stored at the workspace root `screenshots/` folder — from this README they are referenced using `../screenshots/`.

![Open Issues](../screenshots/devtrack_open_issues.png)
Open issues list (GET /api/issues/)

![Create Reporter Request/Response](../screenshots/devtrack_post_reporter.png)
Reporter creation request + response (POST /api/reporters/)

![Failed Issue Create](../screenshots/devtrack_post_issues_Fail.png)
Example of a failed issue creation (validation error)

---

**Troubleshooting**

- If you get JSON decode errors, check that `issues.json` and `reporters.json` contain valid JSON (e.g., `[]` for empty list).
- If `.env` is missing, the default file names (`issues.json`, `reporters.json`) will be used.

---

**Engineering Decisions**

- `TypedDict` for request/response shapes: Using `TypedDict` clarifies and documents the exact expected keys and value types for `Issue` and `Reporter` JSON objects. `TypedDict` is a typing aid rather than a runtime ORM.

- `_ISSUE_KEYS` and `_REPORTER_KEYS` as `frozenset`: The allowed-key sets are stored as `frozenset[str]` so membership checks and set operations are efficient and the collections are immutable. Immutability signals that these are constants and prevents accidental modification at runtime.

---