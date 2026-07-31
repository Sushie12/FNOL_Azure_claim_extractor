from sqlalchemy.orm import Session
from fastapi import UploadFile,HTTPException
from sqlalchemy import or_,asc,desc,func
from enum import Enum

from app.models.claim import Claim
from app.schemas.claim import ClaimListResponse,ClaimResponse

from app.services.extraction_service import extract_to_json_format
UPLOAD_FOLDER = "uploads"

import os
import shutil

from app.logger import logger

def process_claim(file:UploadFile,db:Session):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    logger.info(f"Received upload request for file: {file.filename}") ######Logged

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = extract_to_json_format(file_path)
    
    logger.info("Azure Document Intelligence extraction completed successfully.")  ######Logged

    policy = result["extractedFields"]["Policy Information"]
    incident = result["extractedFields"]["Incident Information"]
    parties = result["extractedFields"]["Involved Parties"]
    asset = result["extractedFields"]["Asset Details"]
    
    #Duplicate claim detection. to detect duplicate records
    existing_claim = check_duplicate_claim(
        db=db,
        policy_number=policy["Policy No."],
        date_of_loss=incident["Date Of Loss"],
        vehicle_plate_number=asset["Vehicle Plate Number"]
   )
    
    if existing_claim:
        raise HTTPException(
            status_code=409, #valid request,but conficts with the existing state of resource
            detail="Duplicate claim detected. This claim already exists."
        )
    
    claim=create_claim(policy,incident,parties,asset,result)
    
    claim_risk_score, risk_level = calculate_claim_risk(
        policy=policy,
        incident=incident,
        asset=asset,
        recommended_route=result["recommendedRoute"]
    )
    claim_status = get_initial_claim_status(
        result["recommendedRoute"]
    )
    
    
    claim.claim_risk_score = claim_risk_score
    claim.risk_level = risk_level
    claim.claim_status=claim_status
    
    db.add(claim)
    db.commit()
    db.refresh(claim)
    logger.info(f"Claim saved successfully. Claim ID: {claim.id}")   ####Logged
    
    return {
        "message":"Cliam uploaded successfully",
        "claimId":claim.id,
        "extractedFields":result["extractedFields"],
        "recommendedRoute":claim.recommended_route,
        "reasoning":claim.reasoning,
        "claimRiskScore": claim.claim_risk_score,
        "riskLevel": claim.risk_level,
        "claimStatus":claim.claim_status
    }
    


def check_duplicate_claim(
    db: Session,
    policy_number: str,
    date_of_loss: str,
    vehicle_plate_number: str
):

    existing_claim = (
        db.query(Claim)
        .filter(
            Claim.policy_number == policy_number,
            Claim.date_of_loss == date_of_loss,
            Claim.vehicle_plate_number == vehicle_plate_number
        )
        .first()
    )

    return existing_claim


def calculate_claim_risk(
    policy: dict,
    incident: dict,
    asset: dict,
    recommended_route: str,
):
    score = 0

    # Rule 1: Duplicate claim
    # if is_duplicate:
    #     score += 40

    # Rule 2: Investigation Flag
    if recommended_route == "Investigation Flag":
        score += 30

    # Rule 3: Manual Review
    elif recommended_route == "Manual Review":
        score += 15

    # Rule 4: High estimated damage
    estimated_damage = incident["Estimated Damage"]

    if estimated_damage != "null":
        amount = float(
            estimated_damage
            .replace(",", "")
            .replace("₹", "")
        )

        if amount > 100000:
            score += 20

    # Rule 5: Missing Policy Number
    if not policy["Policy No."] or policy["Policy No."] == "null":
        score += 10

    # Rule 6: Missing Vehicle Plate
    if not asset["Vehicle Plate Number"] or asset["Vehicle Plate Number"] == "null":
        score += 10

    # Maximum score = 100
    score = min(score, 100)

    # Risk Level
    if score >= 60:
        risk_level = "High"
    elif score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return score, risk_level



def create_claim(
    policy:dict,
    incident:dict,
    parties:dict,
    asset:dict,
    result:dict,
):
    claim = Claim(

        # ---------- Policy Information ----------
        policy_number=policy["Policy No."],
        policyholder_name=policy["PolicyHolder Name"],
        policyholder_email=policy["PolicyHolder Email"],
        carrier=policy["Carrier"],

        # ---------- Incident Information ----------
        date_of_loss=incident["Date Of Loss"],
        loss_time=incident["Time"],
        loss_location=incident["Location"],

        estimated_damage=(
            float(
                incident["Estimated Damage"]
                .replace(",", "")
                .replace("₹", "")
            )
            if incident["Estimated Damage"] != "null"
            else None
        ),

        injured_name=incident["Injured"],

        # ---------- Involved Parties ----------
        agency=parties["Agency"],
        contact_name=parties["Contact Name"],
        contact_email=parties["Contact Email"],

        # ---------- Asset Details ----------
        vehicle_make=asset["Vehicle Make"],
        vehicle_plate_number=asset["Vehicle Plate Number"],

        # ---------- Decision ----------
        recommended_route=result["recommendedRoute"],
        reasoning=result["reasoning"],
        
    )

    return claim
    

# ### For@router get claims
class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class SortField(str, Enum):
    created_at = "created_at"
    estimated_damage = "estimated_damage"
    policyholder_name = "policyholder_name"
    carrier = "carrier"


def list_claims(db, carrier, route, search, sort_by, order, page, size):
    query = db.query(Claim)

    # Filter by carrier
    if carrier:
        query = query.filter(Claim.carrier == carrier)

    # Filter by recommended route
    if route:
        query = query.filter(Claim.recommended_route == route)

    # Filter by search term (case-insensitive search on name or policy number)
    if search:
        query = query.filter(
            or_(
                Claim.policyholder_name.ilike(f"%{search}%"),
                Claim.policy_number.ilike(f"%{search}%"),
            )
        )

    # Mapping of allowed sorting fields
    allowed_sort_fields = {
        "created_at": Claim.created_at,
        "estimated_damage": Claim.estimated_damage,
        "policyholder_name": Claim.policyholder_name,
        "carrier": Claim.carrier,
    }

    # Ensure sort_by and order are either both provided or both omitted
    if (sort_by is None) != (order is None):
        raise HTTPException(
            status_code=400,
            detail="Both 'sort_by' and 'order' must be provided together.",
        )

    # Apply dynamic sorting if both params are present
    if sort_by and order:
        # Extract the enum value string if sort_by is an Enum, otherwise use as-is
        sort_key = getattr(sort_by, "value", sort_by)

        if sort_key not in allowed_sort_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field '{sort_key}'. Allowed values are: {', '.join(allowed_sort_fields.keys())}",
            )

        sort_column = allowed_sort_fields[sort_key]

        # Extract the enum value string if order is an Enum
        order_key = getattr(order, "value", order)

        if str(order_key).lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
    else:
        # Fallback to default sorting (newest first)
        query = query.order_by(desc(Claim.created_at))

    # Pagination calculations
    total_records = query.count()
    total_pages = (total_records + size - 1) // size
    offset = (page - 1) * size

    # Fetch paginated dataset
    claims = query.offset(offset).limit(size).all()

    return ClaimListResponse(
        page=page,
        size=size,
        totalRecords=total_records,
        totalPages=total_pages,
        claims=claims,
    )
    
    
# For route get claim by id
def fetch_claim_by_id(claim_id: int, db: Session):
    claim = db.query(Claim).filter(Claim.id==claim_id).first()
    if claim is None:
        raise HTTPException(
            status_code=404,
            detail="Claim not found"
    )
    return claim


def is_missing(value):
    return value is None or value == "" or value == "null"


def calculate_claim_risk_score(claim: Claim):
    score = 0

    # ---------- Rule 1: High Estimated Damage ----------
    if (
        claim.estimated_damage is not None
        and claim.estimated_damage >= 100000
    ):
        score += 25

    # ---------- Rule 2: AI recommends Investigation ----------
    if claim.recommended_route == "Investigation Flag":
        score += 40

    # ---------- Rule 3: AI recommends Manual Review ----------
    if claim.recommended_route == "Manual Review":
        score += 20

    # ---------- Rule 4: Vehicle Plate Number Missing ----------
    if is_missing(claim.vehicle_plate_number):
        score += 10

    # ---------- Rule 5: Policy Number Missing ----------
    if is_missing(claim.policy_number):
        score += 15

    # ---------- Rule 6: Contact Email Missing ----------
    if is_missing(claim.contact_email):
        score += 5

    # ---------- Rule 7: Loss Location Missing ----------
    if is_missing(claim.loss_location):
        score += 10

    # ---------- Rule 8: Injury + High Damage ----------
    if (
        not is_missing(claim.injured_name)
        and claim.estimated_damage is not None
        and claim.estimated_damage >= 100000
    ):
        score += 15

    # ---------- Final Risk Level ----------
    if score <= 25:
        risk_level = "Low"
    elif score <= 55:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return score, risk_level



def get_initial_claim_status(recommended_route: str):

    if recommended_route == "Investigation Flag":
        return "Investigation In Progress"

    elif recommended_route == "Specialist Queue":
        return "Specialist Assigned"

    return "Pending Review"



def update_claim_status(
    db: Session,
    claim_id: int,
    new_status: str
):
    claim = (
        db.query(Claim)
        .filter(Claim.id == claim_id)
        .first()
    )

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Claim not found."
        )

    valid_statuses = [
        "Pending Review",
        "Investigation In Progress",
        "Specialist Assigned",
        "Approved",
        "Rejected"
    ]

    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid claim status."
        )

    claim.claim_status = new_status

    db.commit()
    db.refresh(claim)

    return claim


def get_dashboard_data(db:Session):
    
    total_claims = db.query(Claim).count()
    
    route_distribution = (
        db.query(
            Claim.recommended_route,
            func.count(Claim.id)
        )
        .group_by(Claim.recommended_route)
        .all()
    )
    route_distribution = [
        {
            "route": route,
            "count": count
        }
        for route, count in route_distribution
    ]
    
    
    
    recent_claims = (
        db.query(Claim)
        .order_by(Claim.created_at.desc())
        .limit(5)
        .all()
    )
    
    average_claim_amount = (
        db.query(func.avg(Claim.estimated_damage))
        .scalar()
    )
    
    highest_claim_amount = (
        db.query(func.max(Claim.estimated_damage))
        .scalar()
    )
    
    average_risk_score = round(
        db.query(func.avg(Claim.claim_risk_score))
        .scalar() or 0,
        2
    )
    
    low_risk = (
        db.query(Claim)
        .filter(Claim.risk_level == "Low")
        .count()
    )

    medium_risk = (
        db.query(Claim)
        .filter(Claim.risk_level == "Medium")
        .count()
    )

    high_risk = total_claims - (low_risk + medium_risk)
    
    highest_risk_score = (
        db.query(func.max(Claim.claim_risk_score))
        .scalar() or 0
    )
    
    carrier_distribution = (
        db.query(
            Claim.carrier,
            func.count(Claim.id)
        )
        .group_by(Claim.carrier)
        .all()
    )
            
    
    return {
    "totalClaims": total_claims,
    "routeDistribution":route_distribution,   
    
    "recentClaims": [
        {
            "id": claim.id,
            "policyholder_name": claim.policyholder_name,
            "carrier": claim.carrier,
            "estimated_damage": claim.estimated_damage,
            "recommended_route": claim.recommended_route,
            "created_at": claim.created_at
        }
        for claim in recent_claims
    ],
    
    "averageClaimAmount":round(average_claim_amount or 0,2),
    "highestClaimAmount":highest_claim_amount or 0,
    
    "averageRiskScore":average_risk_score,
    "highestRiskScore":highest_risk_score,
    
    
    "claimsByRiskLevel":{
        "low":low_risk,
        "medium":medium_risk,
        "high":high_risk
    },
    "carrierDistribution":[
        {
            "carrier": carrier,
            "count": count
        }
        for carrier, count in carrier_distribution
    ]
}
    

