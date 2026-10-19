import pytest
from sqlalchemy import text
from fastapi import UploadFile
from app.database.database import SessionLocal
from app.services.claim_service import process_claim

@pytest.fixture
def db_session():
    """Provides a database session for testing."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.mark.asyncio
async def test_claim_processing_pipeline(db_session):
    # 1. Clean up potential duplicate test record before executing
    db_session.execute(text("DELETE FROM claims WHERE policy_number = 'POL123456';"))
    db_session.commit()

    sample_pdf_path = "pdf10.pdf"

    with open(sample_pdf_path, "rb") as file_bytes:
        upload_file = UploadFile(
            filename="pdf10.pdf",
            file=file_bytes
        )

        # 2. Execute pipeline
        processed_claim = await process_claim(file=upload_file, db=db_session)

        # Print returned keys to verify exact key name during debugging
        print("\n--- RETURNED KEYS ---", processed_claim.keys())

        # 3. Extract claim primary key across possible schema keys
        claim_id = (
            processed_claim.get("id") 
            or processed_claim.get("claim_id") 
            or processed_claim.get("claimId")
        )
        
        if not claim_id and isinstance(processed_claim.get("claim"), dict):
            claim_id = processed_claim["claim"].get("id")

        assert claim_id is not None, f"Claim ID not generated. Output structure: {processed_claim}"