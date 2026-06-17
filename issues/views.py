"""
views.py — DevTrack Issue Tracker API Views

Handles CRUD operations for issues stored in a local JSON file (issues.json).
"""
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from typing import TypedDict, get_type_hints

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Issue, CriticalIssue, LowPriorityIssue


# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Read filename/path from .env
FILE_TO_READ = os.getenv("ISSUES_FILE_NAME", "issues.json")  # Default to issues.json if not set

# Resolve to an absolute path safely
ISSUES_FILE = (BASE_DIR / FILE_TO_READ).resolve()# Load environment variables from .env file
print(ISSUES_FILE)
VALID_STATUSES  = {"open", "in_progress", "closed"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}


# ---------------------------------------------------------------------------
# Canonical shape of an Issue
# ---------------------------------------------------------------------------

class IssueDataType(TypedDict, total=True):
    """
    TypedDict defining the canonical shape of an issue dict.
    All keys are required; extra keys are silently dropped on read/write.
    """

    id:          int
    title:       str
    description: str
    status:      str
    priority:    str
    reporter_id: int


# The set of keys derived directly from the TypedDict — used for whitelist
# filtering so no extra keys ever enter the store.
_ISSUE_KEYS: frozenset[str] = frozenset(get_type_hints(IssueDataType).keys())


def _load_issues_from_file() -> list[IssueDataType]:
    """
    Load and return all issues from the JSON file.
    """
    if not os.path.exists(ISSUES_FILE):
        return []
    try:
        with open(ISSUES_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            print(os.path.exists(ISSUES_FILE))
            if not isinstance(data, list):
                return []
            return [clean_data(item) for item in data if isinstance(item, dict)]
    except (json.JSONDecodeError, OSError):
        return []


def _load_issues_to_file(issues: list[IssueDataType]) -> None:
    """
    Save the given list of issues to the JSON file.

    Args:
        issues: The full list of typed issue dicts to write.

    Raises:
        OSError: If the file cannot be written.
    """
    clean = [clean_data(iss) for iss in issues]
    with open(ISSUES_FILE, "w", encoding="utf-8") as fh:
        json.dump(clean, fh, indent=2, ensure_ascii=False)


def clean_data(data: dict) -> IssueDataType:
    """
    Return a new dict containing **only** the keys declared in
    ``IssueDataType``, discarding any extras.
    """
    return {k: v for k, v in data.items() if k in _ISSUE_KEYS}


def _success(data: IssueDataType | list[IssueDataType] | None, status: int = 200) -> JsonResponse:
    """Wrap *data* in a success envelope and return a JsonResponse."""
    return JsonResponse({"success": True, "data": data, "error": None}, status=status)


def _error(message: str, status: int = 400) -> JsonResponse:
    """Wrap *message* in an error envelope and return a JsonResponse."""
    return JsonResponse({"success": False, "data": None, "error": message}, status=status)


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------
@method_decorator(csrf_exempt, name="dispatch")
class IssueView(View):
    """
    Class-based view for the /api/issues/ endpoint.
    """

    def get(self, request) -> JsonResponse:
        """
        Retrieve issues from the JSON store.
        """
        issues = _load_issues_from_file()
        #print('XXXXXXXXXXXXXXXXXXXXXXX', ISSUES_FILE, FILE_TO_READ)
        # filter by id
        issue_id = request.GET.get("id")
        if issue_id is not None:
            try:
                issue_id = int(issue_id)
            except ValueError:
                return _error("'id' must be an integer.", status=400)

            matched = None
            for current_issue in issues:
                if current_issue.get("id") == issue_id:
                    matched = current_issue
                    break
            # Report error if no issue with the given id is found
            if matched is None:
                print("Issue not found")
                return _error(f"Issue with id={issue_id} not found.", status=404)
            return _success(matched)

        # filter by status
        status_filter = request.GET.get("status")
        if status_filter is not None:
            status_filter = status_filter.lower()
            if status_filter not in VALID_STATUSES:
                return _error(
                    f"Invalid status '{status_filter}'. "
                    f"Choose from: {', '.join(sorted(VALID_STATUSES))}.",
                    status=400,
                )
            issues = [issue for issue in issues if issue.get("status") == status_filter]

        return _success(issues)


    def post(self, request) -> JsonResponse:
        """
        Create a new issue, persist it, and return it with a describe() message.
        """
        print(request.body)
        try:
            body = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return _error("Request body must be valid JSON.", status=400)

        # reject unknown keys
        unknown_keys = set(body.keys()) - _ISSUE_KEYS
        if unknown_keys:
            return _error(
                f"Unknown field(s): {', '.join(sorted(unknown_keys))}. "
                f"Allowed fields: {', '.join(sorted(_ISSUE_KEYS))}.",
                status=400,
            )

        # validate required fields
        title = (body.get("title") or "").strip()
        if not title:
            return _error("'title' is required and must not be empty.", status=400)

        if "reporter_id" not in body:
            return _error("'reporter_id' is required.", status=400)
        try:
            reporter_id = int(body["reporter_id"])
        except (ValueError, TypeError):
            return _error("'reporter_id' must be an integer.", status=400)

        # --- validate optional enum fields -------------------------------
        status = (body.get("status") or "open").strip().lower()
        if status not in VALID_STATUSES:
            return _error(
                f"Invalid status '{status}'. "
                f"Choose from: {', '.join(sorted(VALID_STATUSES))}.",
                status=400,
            )

        priority = (body.get("priority") or "medium").strip().lower()
        if priority not in VALID_PRIORITIES:
            return _error(
                f"Invalid priority '{priority}'. "
                f"Choose from: {', '.join(sorted(VALID_PRIORITIES))}.",
                status=400,
            )

        # --- resolve auto-incremented id ---------------------------------
        issues = _load_issues_from_file()
        new_id = max((issue.get("id", 0) for issue in issues), default=0) + 1

        # --- instantiate the correct Issue subclass ----------------------
        # Pick the subclass concisely for specific priorities.
        issue: Issue = None
        if priority == "critical":
            issue = CriticalIssue(
            id=new_id,
            title=title,
            issue_description=(body.get("description") or "").strip(),
            status=status,
            priority=priority,
            reporter_id=reporter_id,
            created_at=datetime.now(),
        )
        elif priority == "low":
            issue = LowPriorityIssue(
                id=new_id,
                title=title,
                issue_description=(body.get("description") or "").strip(),
                status=status,
                priority=priority,
                reporter_id=reporter_id,
                created_at=datetime.now(),
            )

        issue.validate()

        # Clean the incoming issue data and save to the file.
        typed_issue: IssueDataType = clean_data(issue.to_dict())
        issues.append(typed_issue)
        _load_issues_to_file(issues)

        # Send response back.
        response_data = dict(typed_issue)
        response_data["message"] = issue.describe()

        return JsonResponse({"success": True, "data": response_data, "error": None}, status=201)