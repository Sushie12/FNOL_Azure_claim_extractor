from pydantic import BaseModel,ConfigDict   #BaseModel:Every Pydantic schema inherits from it.
from datetime import datetime
from typing import List

class ClaimResponse(BaseModel):
    id: int

    # ---------- Policy Information ----------
    policy_number: str | None
    policyholder_name: str | None
    policyholder_email: str | None
    carrier: str | None

    # ---------- Incident Information ----------
    date_of_loss: str | None
    loss_time: str | None
    loss_location: str | None
    estimated_damage: float | None
    injured_name: str | None

    # ---------- Involved Parties ----------
    agency: str | None
    contact_name: str | None
    contact_email: str | None

    # ---------- Asset Details ----------
    vehicle_make: str | None
    vehicle_plate_number: str | None

    # ---------- AI Decision ----------
    recommended_route: str | None
    reasoning: str | None
    
    claim_risk_score: int | None
    risk_level: str | None

    claim_status: str | None
    last_updated: datetime | None
    
    reviewer_status_changed:bool|None
    status_updated_by_name: str | None
    status_updated_by_role: str | None

    # ---------- System ----------
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)



class ClaimListResponse(BaseModel):
    page: int
    size: int
    totalRecords: int
    totalPages: int
    claims: List[ClaimResponse]  #"claims is a list, and every item inside it must follow the ClaimResponse schema."

    model_config=ConfigDict(from_attributes=True)
    
class UpdateClaimStatusRequest(BaseModel):
    claim_status: str

