from enum import Enum


class Role(str, Enum):
    ADMIN = "Admin"
    ANALYST = "Analyst"
    REVIEWER = "Reviewer"


# Every status a claim is allowed to hold.
VALID_STATUSES = [
    "Pending Review",
    "Investigation In Progress",
    "Specialist Assigned",
    "Approved",
    "Rejected",
]

# Once a claim reaches one of these, only an Admin may move it again.
TERMINAL_STATUSES = {
    "Approved",
    "Rejected",
}

# Which target statuses each role is allowed to set.
# Analyst is the "maker": triage and investigation only.
# Reviewer is the "checker": the final decision only.
ALLOWED_TRANSITIONS = {
    Role.ADMIN.value: set(VALID_STATUSES),
    Role.ANALYST.value: {
        "Pending Review",
        "Investigation In Progress",
        "Specialist Assigned",
    },
    Role.REVIEWER.value: {
        "Approved",
        "Rejected",
    },
}


def can_set_status(role: str, new_status: str) -> bool:
    return new_status in ALLOWED_TRANSITIONS.get(role, set())


def can_reopen(role: str) -> bool:
    return role == Role.ADMIN.value
