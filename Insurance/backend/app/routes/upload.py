from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from enum import Enum


from app.database.database import get_db
from app.models.claim import Claim
from app.models.users import User

import os

from app.schemas.claim import ClaimListResponse,ClaimResponse,UpdateClaimStatusRequest
from app.services.claim_service import process_claim,list_claims,fetch_claim_by_id,get_dashboard_data,update_claim_status
from app.utils.auth import get_current_user,require_admin,require_uploader,require_any


from app.logger import logger


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class SortField(str, Enum):
    created_at = "created_at"
    estimated_damage = "estimated_damage"
    policyholder_name = "policyholder_name"
    carrier = "carrier"


router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_pdf(
    # file: UploadFile = File(...),
    file: UploadFile = File(...),
    current_user: User = Depends(require_uploader),
    db: Session = Depends(get_db)
):
    print(f"Authenticated user: {current_user.email}")
    result = process_claim(file, db)
    
    return result



@router.get("/claims",response_model=ClaimListResponse)
def get_all_claims(
    carrier: str = None,
    route: str = None,
    search: str = None,
    sort_by: SortField | None=None,
    order: SortOrder | None=None,
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(require_any),
    db: Session = Depends(get_db)
    ):
    return list_claims(
        db=db,
        carrier=carrier,
        route=route,
        search=search,
        sort_by=sort_by,
        order=order,
        page=page,
        size=size
    )

    
    
@router.get("/claims/{claim_id}",response_model=ClaimResponse)
def get_claim_by_id(
    claim_id: int,
    current_user: User = Depends(require_any),
    db: Session = Depends(get_db)
):
    return fetch_claim_by_id(claim_id=claim_id,db=db)



@router.patch("/claims/{claim_id}/status",response_model=ClaimResponse)
def update_status(
    claim_id: int,
    request: UpdateClaimStatusRequest,
    current_user: User = Depends(require_any),
    db: Session = Depends(get_db)
):
    return update_claim_status(
        db=db,
        claim_id=claim_id,
        new_status=request.claim_status,
        role=current_user.role
    )

    
@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(require_any),
    db: Session = Depends(get_db)
):
    return get_dashboard_data(db)
    
