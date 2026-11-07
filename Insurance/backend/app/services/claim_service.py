# from sqlalchemy.orm import Session
# from fastapi import UploadFile,HTTPException
# from sqlalchemy import or_,asc,desc,func
# from enum import Enum

# from app.models.claim import Claim
# from app.schemas.claim import ClaimListResponse,ClaimResponse
# from app.models.users import User

# from app.services.extraction_service import extract_to_json_format
# from app.services.claim_agent import evaluate_claim_with_agent

# UPLOAD_FOLDER = "uploads"

# import os
# import shutil

# from app.logger import logger

# async def process_claim(file: UploadFile, db: Session):
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     logger.info(f"Received upload request for file: {file.filename}")

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     result = extract_to_json_format(file_path)
    
#     logger.info("Azure Document Intelligence extraction completed successfully.")

#     policy = result["extractedFields"]["Policy Information"]
#     incident = result["extractedFields"]["Incident Information"]
#     parties = result["extractedFields"]["Involved Parties"]
#     asset = result["extractedFields"]["Asset Details"]
    
#     # Duplicate claim detection
#     existing_claim = check_duplicate_claim(
#         db=db,
#         policy_number=policy.get("Policy No."),
#         date_of_loss=incident.get("Date Of Loss"),
#         vehicle_plate_number=asset.get("Vehicle Plate Number")
#     )
    
#     if existing_claim:
#         raise HTTPException(
#             status_code=409,
#             detail="Duplicate claim detected. This claim already exists."
#         )
    
#     # Initialize claim record
#     claim = create_claim(policy, incident, parties, asset, result)
    
#     # --- AGENTIC AI EVALUATION (SerpApi + Policy Rules) ---
#     logger.info("Starting Agentic AI evaluation with SerpApi market pricing check...")
    
#     # Parse damage amount strictly from incident
#     raw_estimate = incident.get("Estimated Damage") or 0.0
#     try:
#         estimated_damage = float(str(raw_estimate).replace("₹", "").replace("$", "").replace(",", "").strip())
#     except (ValueError, TypeError):
#         estimated_damage = 0.0

#     # Get vehicle make strictly from asset
#     vehicle_make = asset.get("Vehicle Make") or "Vehicle"
    
#     # Extract City State Zip and Country directly from incident
#     city_state_zip = incident.get("City State Zip") or "null"
#     country = incident.get("Country") or "India"

#     # Call LLM market analyst passing parameters directly
#     agent_assessment = await evaluate_claim_with_agent(
#         vehicle_make=vehicle_make,
#         estimated_damage=estimated_damage,
#         city_state_zip=city_state_zip,
#         country=country
#     )

#     # Attach LLM market reasoning directly to claim object
#     claim.reasoning = agent_assessment.marketReasoning

#     # Save to database
#     db.add(claim)
#     db.commit()
#     db.refresh(claim)
    
#     logger.info(f"Claim saved successfully. Claim ID: {claim.id}")
    
#     return {
#         "message": "Claim uploaded and evaluated successfully",
#         "claimId": claim.id,
#         "extractedFields": result["extractedFields"],
#         "recommendedRoute": claim.recommended_route,
#         "reasoning": claim.reasoning,
#         "claimRiskScore": claim.claim_risk_score,
#         "riskLevel": claim.risk_level,
#         "claimStatus": claim.claim_status
#     }
    


# def check_duplicate_claim(
#     db: Session,
#     policy_number: str,
#     date_of_loss: str,
#     vehicle_plate_number: str
# ):

#     existing_claim = (
#         db.query(Claim)
#         .filter(
#             Claim.policy_number == policy_number,
#             Claim.date_of_loss == date_of_loss,
#             Claim.vehicle_plate_number == vehicle_plate_number
#         )
#         .first()
#     )

#     return existing_claim


# def calculate_claim_risk(
#     policy: dict,
#     incident: dict,
#     asset: dict,
#     recommended_route: str,
# ):
#     score = 0

#     # Rule 1: Duplicate claim
#     # if is_duplicate:
#     #     score += 40

#     # Rule 2: Investigation Flag
#     if recommended_route == "Investigation Flag":
#         score += 30

#     # Rule 3: Manual Review
#     elif recommended_route == "Manual Review":
#         score += 15

#     # Rule 4: High estimated damage
#     estimated_damage = incident["Estimated Damage"]

#     if estimated_damage != "null":
#         amount = float(
#             estimated_damage
#             .replace(",", "")
#             .replace("₹", "")
#         )

#         if amount > 100000:
#             score += 20

#     # Rule 5: Missing Policy Number
#     if not policy["Policy No."] or policy["Policy No."] == "null":
#         score += 10

#     # Rule 6: Missing Vehicle Plate
#     if not asset["Vehicle Plate Number"] or asset["Vehicle Plate Number"] == "null":
#         score += 10

#     # Maximum score = 100
#     score = min(score, 100)

#     # Risk Level
#     if score >= 60:
#         risk_level = "High"
#     elif score >= 30:
#         risk_level = "Medium"
#     else:
#         risk_level = "Low"

#     return score, risk_level



# def create_claim(
#     policy:dict,
#     incident:dict,
#     parties:dict,
#     asset:dict,
#     result:dict,
# ):
#     claim = Claim(

#         # ---------- Policy Information ----------
#         policy_number=policy["Policy No."],
#         policyholder_name=policy["PolicyHolder Name"],
#         policyholder_email=policy["PolicyHolder Email"],
#         carrier=policy["Carrier"],

#         # ---------- Incident Information ----------
#         date_of_loss=incident["Date Of Loss"],
#         loss_time=incident["Time"],
#         # Combine street, city/state, and country safely:
#         loss_location=f'{incident["Street"]}, {incident["CityState"]}, {incident["Country"]}',

#         estimated_damage=(
#             float(
#                 incident["Estimated Damage"]
#                 .replace(",", "")
#                 .replace("₹", "")
#             )
#             if incident["Estimated Damage"] != "null"
#             else None
#         ),

#         injured_name=incident["Injured"],

#         # ---------- Involved Parties ----------
#         agency=parties["Agency"],
#         contact_name=parties["Contact Name"],
#         contact_email=parties["Contact Email"],

#         # ---------- Asset Details ----------
#         vehicle_make=asset["Vehicle Make"],
#         vehicle_plate_number=asset["Vehicle Plate Number"],

#         # ---------- Decision ----------
#         recommended_route=result["recommendedRoute"],
#         reasoning=result["reasoning"],
        
#     )

#     return claim
    

# # ### For@router get claims
# class SortOrder(str, Enum):
#     asc = "asc"
#     desc = "desc"

# class SortField(str, Enum):
#     created_at = "created_at"
#     estimated_damage = "estimated_damage"
#     policyholder_name = "policyholder_name"
#     carrier = "carrier"


# def list_claims(db, carrier, route, search, sort_by, order, page, size):
#     query = db.query(Claim)

#     # Filter by carrier
#     if carrier:
#         query = query.filter(Claim.carrier == carrier)

#     # Filter by recommended route
#     if route:
#         query = query.filter(Claim.recommended_route == route)

#     # Filter by search term (case-insensitive search on name or policy number)
#     if search:
#         query = query.filter(
#             or_(
#                 Claim.policyholder_name.ilike(f"%{search}%"),
#                 Claim.policy_number.ilike(f"%{search}%"),
#             )
#         )

#     # Mapping of allowed sorting fields
#     allowed_sort_fields = {
#         "created_at": Claim.created_at,
#         "estimated_damage": Claim.estimated_damage,
#         "policyholder_name": Claim.policyholder_name,
#         "carrier": Claim.carrier,
#     }

#     # Ensure sort_by and order are either both provided or both omitted
#     if (sort_by is None) != (order is None):
#         raise HTTPException(
#             status_code=400,
#             detail="Both 'sort_by' and 'order' must be provided together.",
#         )

#     # Apply dynamic sorting if both params are present
#     if sort_by and order:
#         # Extract the enum value string if sort_by is an Enum, otherwise use as-is
#         sort_key = getattr(sort_by, "value", sort_by)

#         if sort_key not in allowed_sort_fields:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid sort field '{sort_key}'. Allowed values are: {', '.join(allowed_sort_fields.keys())}",
#             )

#         sort_column = allowed_sort_fields[sort_key]

#         # Extract the enum value string if order is an Enum
#         order_key = getattr(order, "value", order)

#         if str(order_key).lower() == "desc":
#             query = query.order_by(desc(sort_column))
#         else:
#             query = query.order_by(asc(sort_column))
#     else:
#         # Fallback to default sorting (newest first)
#         query = query.order_by(desc(Claim.created_at))

#     # Pagination calculations
#     total_records = query.count()
#     total_pages = (total_records + size - 1) // size
#     offset = (page - 1) * size

#     # Fetch paginated dataset
#     claims = query.offset(offset).limit(size).all()

#     return ClaimListResponse(
#         page=page,
#         size=size,
#         totalRecords=total_records,
#         totalPages=total_pages,
#         claims=claims,
#     )
    
    
# # For route get claim by id
# def fetch_claim_by_id(claim_id: int, db: Session):
#     claim = db.query(Claim).filter(Claim.id==claim_id).first()
#     if claim is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Claim not found"
#     )
#     return claim


# def is_missing(value):
#     return value is None or value == "" or value == "null"


# def calculate_claim_risk_score(claim: Claim):
#     score = 0

#     # ---------- Rule 1: High Estimated Damage ----------
#     if (
#         claim.estimated_damage is not None
#         and claim.estimated_damage >= 100000
#     ):
#         score += 25

#     # ---------- Rule 2: AI recommends Investigation ----------
#     if claim.recommended_route == "Investigation Flag":
#         score += 40

#     # ---------- Rule 3: AI recommends Manual Review ----------
#     if claim.recommended_route == "Manual Review":
#         score += 20

#     # ---------- Rule 4: Vehicle Plate Number Missing ----------
#     if is_missing(claim.vehicle_plate_number):
#         score += 10

#     # ---------- Rule 5: Policy Number Missing ----------
#     if is_missing(claim.policy_number):
#         score += 15

#     # ---------- Rule 6: Contact Email Missing ----------
#     if is_missing(claim.contact_email):
#         score += 5

#     # ---------- Rule 7: Loss Location Missing ----------
#     if is_missing(claim.loss_location):
#         score += 10

#     # ---------- Rule 8: Injury + High Damage ----------
#     if (
#         not is_missing(claim.injured_name)
#         and claim.estimated_damage is not None
#         and claim.estimated_damage >= 100000
#     ):
#         score += 15

#     # ---------- Final Risk Level ----------
#     if score <= 25:
#         risk_level = "Low"
#     elif score <= 55:
#         risk_level = "Medium"
#     else:
#         risk_level = "High"

#     return score, risk_level



# def get_initial_claim_status(recommended_route: str):

#     if recommended_route == "Fast-Track":
#         return "Auto Approved"

#     elif recommended_route == "Manual Review":
#         return "Pending Review"

#     elif recommended_route == "Investigation Flag":
#         return "Pending Investigation"

#     elif recommended_route == "Specialist Queue":
#         return "Escalated"

#     return "Pending Review"



# def update_claim_status(
#     db: Session,
#     claim_id: int,
#     new_status: str,
#     current_user:User
# ):
#     claim = (
#         db.query(Claim)
#         .filter(Claim.id == claim_id)
#         .first()
#     )

#     if not claim:
#         raise HTTPException(
#             status_code=404,
#             detail="Claim not found."
#         )
    
#     valid_statuses = [
#         "Approved",
#         "Rejected",
#         "Escalated"
#     ]
    
#     if new_status not in valid_statuses:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid claim status."
#         )
    
        
#     # Reviewer can update only once
#     if current_user.role == "Reviewer":
#         if claim.reviewer_status_changed:
#             raise HTTPException(
#                 status_code=403,
#                 detail="Reviewer has already updated the status for this claim."
#             )

#         claim.reviewer_status_changed = True

#     #Update status
#     claim.claim_status = new_status
#     claim.status_updated_by_name = current_user.full_name
#     claim.status_updated_by_role = current_user.role

#     db.commit()
#     db.refresh(claim)

#     return claim


# def get_dashboard_data(db:Session):
    
#     total_claims = db.query(Claim).count()
#     pending_review = (
#     db.query(Claim)
#     .filter(Claim.claim_status == "Pending Review")
#     .count()
#     )

#     approved = (
#         db.query(Claim)
#         .filter(
#             Claim.claim_status.in_(["Approved", "Auto Approved"])
#         )
#         .count()
#     )

#     rejected = (
#         db.query(Claim)
#         .filter(Claim.claim_status == "Rejected")
#         .count()
#     )
    
    
#     route_distribution = (
#         db.query(
#             Claim.recommended_route,
#             func.count(Claim.id)
#         )
#         .group_by(Claim.recommended_route)
#         .all()
#     )
#     route_distribution = [
#         {
#             "route": route,
#             "count": count
#         }
#         for route, count in route_distribution
#     ]

    
#     recent_claims = (
#         db.query(Claim)
#         .order_by(Claim.created_at.desc())
#         .limit(5)
#         .all()
#     )
    
#     average_claim_amount = (
#         db.query(func.avg(Claim.estimated_damage))
#         .scalar()
#     )
    
#     highest_claim_amount = (
#         db.query(func.max(Claim.estimated_damage))
#         .scalar()
#     )
    
#     average_risk_score = round(
#         db.query(func.avg(Claim.claim_risk_score))
#         .scalar() or 0,
#         2
#     )
    
#     low_risk = (
#         db.query(Claim)
#         .filter(Claim.risk_level == "Low")
#         .count()
#     )

#     medium_risk = (
#         db.query(Claim)
#         .filter(Claim.risk_level == "Medium")
#         .count()
#     )

#     high_risk = total_claims - (low_risk + medium_risk)
    
#     highest_risk_score = (
#         db.query(func.max(Claim.claim_risk_score))
#         .scalar() or 0
#     )
    
#     carrier_distribution = (
#         db.query(
#             Claim.carrier,
#             func.count(Claim.id)
#         )
#         .group_by(Claim.carrier)
#         .all()
#     )
            
    
#     return {
#     "totalClaims": total_claims,
#     "pendingReview": pending_review,
#     "approved": approved,
#     "rejected": rejected,
#     "routeDistribution":route_distribution,   
    
#     "recentClaims": [
#         {
#             "id": claim.id,
#             "policyholder_name": claim.policyholder_name,
#             "carrier": claim.carrier,
#             "estimated_damage": claim.estimated_damage,
#             "recommended_route": claim.recommended_route,
#             "claim_status":claim.claim_status,
#             "created_at": claim.created_at
#         }
#         for claim in recent_claims
#     ],
    
#     "averageClaimAmount":round(average_claim_amount or 0,2),
#     "highestClaimAmount":highest_claim_amount or 0,
    
#     "averageRiskScore":average_risk_score,
#     "highestRiskScore":highest_risk_score,
    
    
#     "claimsByRiskLevel":{
#         "low":low_risk,
#         "medium":medium_risk,
#         "high":high_risk
#     },
#     "carrierDistribution":[
#         {
#             "carrier": carrier,
#             "count": count
#         }
#         for carrier, count in carrier_distribution
#     ]
# }
    


from enum import Enum
from fastapi import UploadFile, HTTPException
from sqlalchemy import or_, asc, desc, func
from sqlalchemy.orm import Session

from app.logger import logger

# ---------------------------------------------------------------------
# 1. IMPORTS FIXED: Import SQLAlchemy Model + Pydantic Schemas
# ---------------------------------------------------------------------
from app.models.claim import Claim
from app.schemas.claim import (
    ExtractedFieldsSchema,
    ClaimUploadResponse,
    ClaimListResponse,
)
from app.models.users import User
from app.services.claim_agent import evaluate_claim_with_agent
from app.services.extraction_service import extract_acord_data


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class SortField(str, Enum):
    created_at = "created_at"
    estimated_damage = "estimated_damage"
    policyholder_name = "policyholder_name"
    carrier = "carrier"


# =====================================================================
# 1. PROCESS CLAIM WORKFLOW
# =====================================================================

async def process_claim(file: UploadFile, db: Session):
    logger.info(f"Processing claim for uploaded file: {file.filename}")

    # Step 1: Extraction using extract_acord_data
    result = extract_acord_data(file.file)
    
    fields = {
        name: item.get("value") if isinstance(item, dict) else item
        for name, item in result.items()
    }

    # Step 2: Mandatory Fields Check (Simple empty string check)
    mandatory_map = {
        "Policy No": fields.get("policy_number"),
        "Policyholder Name": fields.get("insured_name"),
        "Carrier": fields.get("carrier"),
        "Estimate Amount": fields.get("vehicle_estimateAmount"),
    }
    missing = [
        key for key, val in mandatory_map.items() 
        if not str(val or "").strip()
    ]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot process this claim. Missing mandatory field(s): {', '.join(missing)}."
        )

    # Step 3: Duplicate Claim Check
    policy_no = str(fields["policy_number"]).strip()
    existing_claim = (
        db.query(Claim)
        .filter(func.upper(Claim.policy_number) == policy_no.upper())
        .first()
    )
    if existing_claim:
        raise HTTPException(
            status_code=409,
            detail="Duplicate claim detected. This claim already exists."
        )

    # Step 4: Location & Agent Evaluation
    loss_citystatezip = str(fields.get("loss_citystatezip") or "").strip()
    loss_country = str(fields.get("loss_country") or "India").strip()
    estimated_damage = float(fields.get("vehicle_estimateAmount") or 0.0)
    vehicle_make = fields.get("vehicle_make") or "Vehicle"

    agent_assessment = await evaluate_claim_with_agent(
        vehicle_make=vehicle_make,
        estimated_damage=estimated_damage,
        city_state_zip=loss_citystatezip,
        country=loss_country
    )

    # Step 5: Check Investigation Flag & Specialist Queue First
    target_text = " ".join([
        str(fields.get("loss_description") or ""),
        str(fields.get("vehicle_damage") or ""),
        str(fields.get("damaged_damage") or ""),
        str(fields.get("remarks") or ""),
    ]).lower()

    fraud_keywords = ["fraud", "inconsistent", "flagged"]
    detected_fraud_words = [word for word in fraud_keywords if word in target_text]

    injured = fields.get("injured_name1") or fields.get("injured_name")
    has_injured = injured is not None and str(injured).strip() != ""

    pre_route = None
    if detected_fraud_words:
        pre_route = "Investigation Flag"
    elif has_injured:
        pre_route = "Specialist Queue"

    # Step 6: Risk Calculation (Only if pre_route is None)
    factors = []
    saved_score = None
    risk_level = None
    raw_score = 0

    if pre_route is not None:
        final_route = pre_route
    else:
        raw_score, saved_score, risk_level, final_route, factors = calculate_risk_and_route(fields)

    # Build Reasoning Summary
    reason_parts = []
    if final_route == "Investigation Flag":
        reason_parts.append(f"Flagged text keywords detected ({', '.join(detected_fraud_words)}), routed to Investigation Flag.")
    elif final_route == "Specialist Queue":
        reason_parts.append(f"Injured person reported ({injured}), routed to Specialist Queue.")
    elif final_route == "Fast-Track":
        reason_parts.append("No risk factors present. Claim fast-tracked.")
    else:
        reason_parts.append(f"Routed to {final_route}.")

    if factors:
        reason_parts.append(f"Risk score {raw_score}/100: " + "; ".join(f"{txt} (+{pts})" for txt, pts in factors) + ".")
    elif pre_route is None:
        reason_parts.append(f"Risk score {raw_score}/100: No secondary risk factors.")

    if agent_assessment and getattr(agent_assessment, "marketReasoning", None):
        reason_parts.append(f"Market check: {agent_assessment.marketReasoning}")

    full_reasoning = " ".join(reason_parts)
    initial_status = "Accepted" if final_route == "Fast-Track" else "Escalated"

    # ---------------------------------------------------------------------
    # Step 7: FIX - Create SQLAlchemy ORM Model Instance for Database Storage
    # ---------------------------------------------------------------------
    db_claim = Claim(
        policy_number=policy_no,
        policyholder_name=fields.get("insured_name"),
        carrier=fields.get("carrier"),
        estimated_damage=estimated_damage,
        recommended_route=final_route,
        reasoning=full_reasoning,
        claim_risk_score=saved_score,
        risk_level=risk_level,
        claim_status=initial_status,
        
        # Cleaned JSON containing ONLY populated keys
        raw_extracted_fields=fields
    )

    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)

    logger.info(f"Claim saved successfully with ID: {db_claim.id}")

    # Return structured dict response matching frontend expectations
    return {
        "message": "Claim uploaded and evaluated successfully",
        "claimId": db_claim.id,
        "extractedFields": fields,
        "recommendedRoute": db_claim.recommended_route,
        "reasoning": db_claim.reasoning,
        "claimRiskScore": db_claim.claim_risk_score,
        "riskLevel": db_claim.risk_level,
        "claimStatus": db_claim.claim_status
    }


# =====================================================================
# 2. RISK CALCULATION & BUCKET ROUTING METHOD
# =====================================================================

def calculate_risk_and_route(fields: dict):
    v_est = float(fields.get("vehicle_estimateAmount") or 0.0)
    d_est = float(fields.get("damaged_estimateAmount") or 0.0)
    total_estimate = v_est + d_est

    # 1. Estimate Risk Points based on damage threshold
    if total_estimate <= 40000:
        est_pts = 30
    elif total_estimate <= 80000:
        est_pts = 50
    elif total_estimate <= 200000:
        est_pts = 70
    else:
        est_pts = 120

    flag_points = {
        "vehicle_permission": 30,
        "damaged_non_vehicle": 30,
        "damaged_plateNo": 40,
        "loss_policeorfirecontacted": 30,
        "vehicle_childSeatLoss": 30,
    }

    min_raw = 30
    max_raw = 120 + sum(flag_points.values())  # 120 + 160 = 280

    raw_flag_score = 0
    triggered_flags = []

    # Check for "✔" (not ticked = flag)
    if str(fields.get("vehicle_permission") or "").strip() != "✔":
        raw_flag_score += flag_points["vehicle_permission"]
        triggered_flags.append(("vehicle driven without permission", flag_points["vehicle_permission"]))

    # Check for "✔" (ticked = flag)
    if str(fields.get("damaged_non_vehicle") or "").strip() == "✔":
        raw_flag_score += flag_points["damaged_non_vehicle"]
        triggered_flags.append(("other party's non-vehicle property damaged", flag_points["damaged_non_vehicle"]))

    # Check non-empty plate number
    plate = fields.get("damaged_plateNo")
    if plate is not None and str(plate).strip() != "":
        raw_flag_score += flag_points["damaged_plateNo"]
        triggered_flags.append(("other vehicle involved (damaged plate number given)", flag_points["damaged_plateNo"]))

    # Check empty police contact status
    if not str(fields.get("loss_policeorfirecontacted") or "").strip():
        raw_flag_score += flag_points["loss_policeorfirecontacted"]
        triggered_flags.append(("police/fire department not contacted", flag_points["loss_policeorfirecontacted"]))

    # Check for "✔" (ticked = flag)
    if str(fields.get("vehicle_childSeatLoss") or "").strip() == "✔":
        raw_flag_score += flag_points["vehicle_childSeatLoss"]
        triggered_flags.append(("child seat sustained a loss", flag_points["vehicle_childSeatLoss"]))

    # Total raw score & 0-100 scaled score
    raw_score = est_pts + raw_flag_score
    scaled_score = round((raw_score - min_raw) / (max_raw - min_raw) * 100)

    # 2. Build factors list ONCE at the end
    factors = []

    # Include damage estimate factor if above lowest tier
    if est_pts > min_raw:
        scaled_est = round((est_pts - min_raw) / (max_raw - min_raw) * 100)
        factors.append((f"total estimate Rs.{total_estimate:,.0f}", scaled_est))

    # Include flag factors
    for text, pts in triggered_flags:
        scaled_flag_pts = round(pts / (max_raw - min_raw) * 100)
        factors.append((text, scaled_flag_pts))

    # 3. Bucket Routing Assignment
    if scaled_score == 0:
        route = "Fast-Track"
        risk_level = "Low"
    elif scaled_score <= 19:
        route = "Manual Review - Low"
        risk_level = "Low"
    elif scaled_score <= 35:
        route = "Manual Review - Medium"
        risk_level = "Medium"
    else:
        route = "Manual Review - High"
        risk_level = "High"

    return raw_score, scaled_score, risk_level, route, factors


# =====================================================================
# 3. STATUS UPDATE SERVICE
# =====================================================================

def update_claim_status(db: Session, claim_id: int, new_status: str, current_user: User):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found.")

    # Access control: Reviewer can update status ONCE; Admin can update MULTIPLE times
    if current_user.role == "Reviewer":
        if claim.reviewer_status_changed:
            raise HTTPException(
                status_code=403,
                detail="Reviewer has already updated the status for this claim."
            )
        claim.reviewer_status_changed = True
    elif current_user.role != "Admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update claim status."
        )

    claim.claim_status = new_status
    claim.status_updated_by_name = current_user.full_name
    claim.status_updated_by_role = current_user.role

    db.commit()
    db.refresh(claim)

    return claim


# =====================================================================
# 4. READ & LIST CLAIMS SERVICES
# =====================================================================

def list_claims(db: Session, carrier, route, search, sort_by, order, page: int, size: int):
    query = db.query(Claim)

    if carrier:
        query = query.filter(Claim.carrier == carrier)
    if route:
        query = query.filter(Claim.recommended_route == route)
    if search:
        query = query.filter(
            or_(
                Claim.policyholder_name.ilike(f"%{search}%"),
                Claim.policy_number.ilike(f"%{search}%"),
            )
        )

    allowed_sort_fields = {
        "created_at": Claim.created_at,
        "estimated_damage": Claim.estimated_damage,
        "policyholder_name": Claim.policyholder_name,
        "carrier": Claim.carrier,
    }

    if sort_by and order:
        sort_key = getattr(sort_by, "value", sort_by)
        sort_column = allowed_sort_fields.get(sort_key, Claim.created_at)
        order_key = getattr(order, "value", order)

        if str(order_key).lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(Claim.id))

    total_records = query.count()
    total_pages = (total_records + size - 1) // size
    offset = (page - 1) * size

    claims = query.offset(offset).limit(size).all()

    
    return ClaimListResponse(
        page=page,
        size=size,
        totalRecords=total_records,
        totalPages=total_pages,
        claims=claims
    )


def fetch_claim_by_id(claim_id: int, db: Session):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim