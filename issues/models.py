from abc import ABC, abstractmethod

class BaseEntity(ABC):
    @abstractmethod
    def validate(self):
        pass

    def to_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
        }

class Reporter(BaseEntity):
    """
    Represnts the Reporter of Issue.
    """
    def __init__(
        self,
        id: str,
        name: str,
        email: str,
        team: str,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not self.name:
            raise ValueError('Name cannot be empty')
        if '@' not in self.email:
            raise ValueError('Invalid email')


class Issue(BaseEntity):
    """
    Represents an issue in the system.
    Attributes:
        id (str): Unique identifier for the issue.
        title (str): Title of the issue.
        description (str): Detailed description of the issue.
        status (str): Current status of the issue (e.g., "open", "closed").
        priority (int): Priority level of the issue (e.g., 1 for high, 2 for medium, 3 for low).
        reporter_id (int): ID of the reporter who created the issue.
        created_at (str): Timestamp when the issue was created.
    """
    
    VALID_STATUSES = {"open", "in_progress", "closed"}
    VALID_PRIORITIES = {"low", "medium", "high", "critical"}

    def __init__(
        self,
        id: str,
        title: str,
        issue_description: str,
        status: str,
        priority: str,
        reporter_id: int,
        created_at: str | None,
    ):
        self.id = id
        self.title = title
        self.description = issue_description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        self.created_at = created_at

    def describe(self):
        """
        Returns a human-readable description of the issue.
        """
        return f"{self.title} [{self.priority}]"

    def validate(self) -> None:
        """
        Validate issue fields. Raises ValueError on invalid data.
        """
        if not (isinstance(self.title, str) and self.title.strip()):
            raise ValueError("'title' is required and must not be empty")

        if not isinstance(self.reporter_id, int):
            raise ValueError("'reporter_id' must be an integer")

        if not isinstance(self.status, str) or self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{self.status}'. Choose from: {', '.join(sorted(self.VALID_STATUSES))}.")

        if not isinstance(self.priority, str) or self.priority not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{self.priority}'. Choose from: {', '.join(sorted(self.VALID_PRIORITIES))}.")


class CriticalIssue(Issue):
    """
    Represents a critical issue in the system.
    """
    
    def describe(self):
        return f"[URGENT] {self.title} — needs immediate attention"

class LowPriorityIssue(Issue):
    """
    Represents a low-priority issue in the system.
    """
    def describe(self):
        return f"{self.title} — low priority, handle when free"