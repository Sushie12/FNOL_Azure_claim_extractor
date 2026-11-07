from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from app.models.claim import Claim


def get_dashboard_data(db: Session):
    total_claims = db.query(Claim).count()

    if total_claims == 0:
        return {
            "totalClaims": 0,
            "statusDistribution": {"approved": 0, "escalated": 0, "rejected": 0},
            "routeDistribution": {},
            "averageClaimAmount": 0.0,
            "highestClaimAmount": 0.0,
            "lowestClaimAmount": 0.0,
            "mostFrequentCarrier": "N/A",
            "averageRiskScore": 0.0,
            "highestRiskScore": 0,
            "claimsByRiskLevel": {"low": 0, "medium": 0, "high": 0},
            "carrierDistribution": [],
            "recentClaims": []
        }

    # 1. Status Counts (Approved, Escalated, Rejected)
    status_counts_raw = (
        db.query(Claim.claim_status, func.count(Claim.id))
        .group_by(Claim.claim_status)
        .all()
    )
    status_distribution = {"approved": 0, "escalated": 0, "rejected": 0}
    for status_name, count in status_counts_raw:
        if status_name:
            status_distribution[status_name.lower()] = count

    # 2. Recommended Route Counts
    route_counts_raw = (
        db.query(Claim.recommended_route, func.count(Claim.id))
        .group_by(Claim.recommended_route)
        .all()
    )
    route_distribution = {route: count for route, count in route_counts_raw if route}

    # 3. Damage Amount Stats
    damage_stats = (
        db.query(
            func.avg(Claim.estimated_damage),
            func.max(Claim.estimated_damage),
            func.min(Claim.estimated_damage),
        )
        .first()
    )
    avg_damage = round(damage_stats[0] or 0.0, 2)
    max_damage = damage_stats[1] or 0.0
    min_damage = damage_stats[2] or 0.0

    # 4. Most Frequent Carrier Name
    top_carrier_row = (
        db.query(Claim.carrier, func.count(Claim.id).label("carrier_count"))
        .filter(Claim.carrier.isnot(None), Claim.carrier != "")
        .group_by(Claim.carrier)
        .order_by(desc("carrier_count"))
        .first()
    )
    most_frequent_carrier = top_carrier_row[0] if top_carrier_row else "N/A"

    # 5. Risk Score & Risk Level Breakdown
    risk_stats = (
        db.query(
            func.avg(Claim.claim_risk_score),
            func.max(Claim.claim_risk_score)
        )
        .first()
    )
    avg_risk_score = round(risk_stats[0] or 0.0, 2)
    max_risk_score = risk_stats[1] or 0

    risk_level_raw = (
        db.query(Claim.risk_level, func.count(Claim.id))
        .group_by(Claim.risk_level)
        .all()
    )
    risk_level_distribution = {"low": 0, "medium": 0, "high": 0}
    for level, count in risk_level_raw:
        if level:
            risk_level_distribution[level.lower()] = count

    # 6. Carrier Distribution List (for Charts)
    carrier_distribution = (
        db.query(Claim.carrier, func.count(Claim.id))
        .group_by(Claim.carrier)
        .all()
    )
    carrier_list = [
        {"carrier": carrier or "Unknown", "count": count}
        for carrier, count in carrier_distribution
    ]

    # 7. Recent 5 Claims Feed
    recent_claims = (
        db.query(Claim)
        .order_by(Claim.created_at.desc())
        .limit(5)
        .all()
    )
    recent_claims_data = [
        {
            "id": claim.id,
            "policyNumber": claim.policy_number,
            "policyholderName": claim.policyholder_name,
            "carrier": claim.carrier,
            "estimatedDamage": claim.estimated_damage,
            "recommendedRoute": claim.recommended_route,
            "claimStatus": claim.claim_status,
            "riskLevel": claim.risk_level,
            "createdAt": claim.created_at
        }
        for claim in recent_claims
    ]

    return {
        "totalClaims": total_claims,
        "statusDistribution": status_distribution,
        "routeDistribution": route_distribution,
        "averageClaimAmount": avg_damage,
        "highestClaimAmount": max_damage,
        "lowestClaimAmount": min_damage,
        "mostFrequentCarrier": most_frequent_carrier,
        "averageRiskScore": avg_risk_score,
        "highestRiskScore": max_risk_score,
        "claimsByRiskLevel": risk_level_distribution,
        "carrierDistribution": carrier_list,
        "recentClaims": recent_claims_data
    }