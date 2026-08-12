"""RBAC matrix test. Run from backend/: pytest test_rbac.py -v"""
import os

os.environ.setdefault("postgre_database_url", "sqlite:///./test_rbac.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
# Azure client is built at import time; dummy values keep the import working.
os.environ.setdefault("azure_endpoint", "https://example.cognitiveservices.azure.com/")
os.environ.setdefault("azure_key", "dummy-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.main import app
from app.models.claim import Claim
from app.models.users import User
from app.utils.security import hash_password

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

USERS = [
    ("admin@insurance.com", "Admin@123", "Admin"),
    ("analyst@insurance.com", "Analyst@123", "Analyst"),
    ("reviewer@insurance.com", "Reviewer@123", "Reviewer"),
]


@pytest.fixture(scope="module", autouse=True)
def seed():
    db = TestingSession()
    for email, password, role in USERS:
        db.add(
            User(
                full_name=role,
                email=email,
                password_hash=hash_password(password),
                role=role,
                is_active=True,
            )
        )
    db.commit()
    db.close()


def token(email, password):
    response = client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def headers(role):
    email, password, _ = next(u for u in USERS if u[2] == role)
    return {"Authorization": f"Bearer {token(email, password)}"}


def new_claim(status="Pending Review"):
    db = TestingSession()
    claim = Claim(policy_number="P-1", claim_status=status)
    db.add(claim)
    db.commit()
    claim_id = claim.id
    db.close()
    return claim_id


def test_login_returns_role_in_me():
    for email, password, role in USERS:
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token(email, password)}"},
        )
        assert response.status_code == 200
        assert response.json()["role"] == role


def test_reads_require_a_token():
    assert client.get("/claims").status_code in (401, 403)
    assert client.get("/dashboard").status_code in (401, 403)


@pytest.mark.parametrize("role", ["Admin", "Analyst", "Reviewer"])
def test_all_roles_can_read(role):
    assert client.get("/claims", headers=headers(role)).status_code == 200


def test_reviewer_cannot_upload():
    response = client.post(
        "/upload",
        headers=headers("Reviewer"),
        files={"file": ("a.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert response.status_code == 403
    assert "Reviewer" in response.json()["detail"]


@pytest.mark.parametrize(
    "role,target,expected",
    [
        ("Analyst", "Investigation In Progress", 200),
        ("Analyst", "Specialist Assigned", 200),
        ("Analyst", "Approved", 403),
        ("Analyst", "Rejected", 403),
        ("Reviewer", "Approved", 200),
        ("Reviewer", "Rejected", 200),
        ("Reviewer", "Investigation In Progress", 403),
        ("Admin", "Approved", 200),
        ("Admin", "Investigation In Progress", 200),
    ],
)
def test_status_transition_matrix(role, target, expected):
    claim_id = new_claim()
    response = client.patch(
        f"/claims/{claim_id}/status",
        headers=headers(role),
        json={"claim_status": target},
    )
    assert response.status_code == expected, response.text


def test_only_admin_can_reopen_a_decided_claim():
    claim_id = new_claim(status="Approved")
    denied = client.patch(
        f"/claims/{claim_id}/status",
        headers=headers("Analyst"),
        json={"claim_status": "Investigation In Progress"},
    )
    assert denied.status_code == 403

    allowed = client.patch(
        f"/claims/{claim_id}/status",
        headers=headers("Admin"),
        json={"claim_status": "Pending Review"},
    )
    assert allowed.status_code == 200


def test_invalid_status_is_rejected_before_role_check():
    claim_id = new_claim()
    response = client.patch(
        f"/claims/{claim_id}/status",
        headers=headers("Admin"),
        json={"claim_status": "Nonsense"},
    )
    assert response.status_code == 400
