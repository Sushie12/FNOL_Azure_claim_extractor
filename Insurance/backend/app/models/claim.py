from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime

from app.database.database import Base


class Claim(Base):
    __tablename__ = "claims"

    # ---------- Primary Key ----------
    id = Column(Integer, primary_key=True, index=True)

    # ---------- Policy Information ----------
    policy_number = Column(String(100), nullable=True)
    policyholder_name = Column(String(100), nullable=True)
    policyholder_email = Column(String(150), nullable=True)
    carrier = Column(String(100), nullable=True)

    # ---------- Incident Information ----------
    date_of_loss = Column(String(50), nullable=True)
    loss_time = Column(String(50), nullable=True)
    loss_location = Column(String(255), nullable=True)
    estimated_damage = Column(Float, nullable=True)
    injured_name = Column(String(150), nullable=True)

    # ---------- Involved Parties ----------
    agency = Column(String(150), nullable=True)
    contact_name = Column(String(150), nullable=True)
    contact_email = Column(String(150), nullable=True)

    # ---------- Asset Details ----------
    vehicle_make = Column(String(100), nullable=True)
    vehicle_plate_number = Column(String(100), nullable=True)

    # ---------- Decision ----------
    recommended_route = Column(String(100), nullable=True)
    reasoning = Column(Text, nullable=True)
    
    #----------Claim risk------------
    claim_risk_score = Column(Integer, nullable=True)
    risk_level = Column(String(20), nullable=True)
    
    # ---------- Claim Workflow ----------
    claim_status = Column(String(30), nullable=True)

    last_updated = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # ---------- System ----------
    created_at = Column(DateTime, default=datetime.utcnow)