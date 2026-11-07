from pydantic import BaseModel,ConfigDict   #BaseModel:Every Pydantic schema inherits from it.
from datetime import datetime
from typing import List, Any, Dict


class ExtractedFieldsSchema(BaseModel):
    # Core Identification & Policy
    policy_number: str | None = None
    insured_name: str | None = None
    insured_email1: str | None = None
    insured_email2: str | None = None
    insured_dob: str | None = None
    insured_marital: str | None = None
    insured_fein: str | None = None
    insured_location_code: str | None = None
    insured_phone1: str | None = None
    insured_phone1_home: str | None = None
    insured_phone1_bus: str | None = None
    insured_phone2: str | None = None
    insured_phone2_home: str | None = None
    insured_phone2_bus: str | None = None
    carrier: str | None = None
    carrier_lineofbusiness: str | None = None
    carrier_NAIC: str | None = None

    # Agency & Contact Details
    agency: str | None = None
    agency_code: str | None = None
    agency_subcode: str | None = None
    agency_customer_id: str | None = None
    agency_contact_name: str | None = None
    agency_email: str | None = None
    agency_phone: str | None = None
    agency_fax: str | None = None
    contact_name: str | None = None
    contact_email1: str | None = None
    contact_email2: str | None = None
    contact_phone1: str | None = None
    contact_phone1_home: str | None = None
    contact_phone1_bus: str | None = None
    contact_phone2: str | None = None
    contact_phone2_home: str | None = None
    contact_phone2_bus: str | None = None
    contact_is_insured: str | None = None
    contact_whentocontact: str | None = None

    # Incident & Loss Details
    date_of_loss: str | None = None
    time_of_loss: str | None = None
    time_of_loss_AM: str | None = None
    loss_street: str | None = None
    loss_citystatezip: str | None = None
    loss_country: str | None = None
    loss_description: str | None = None
    loss_policeorfirecontacted: str | None = None
    loss_reportno: str | None = None
    loss_locationIfNotPresent: str | None = None
    reported_by: str | None = None
    reported_to: str | None = None
    form_created_date: str | None = None
    remarks: str | None = None

    # Vehicle (Insured Asset) Details
    vehicle_make: str | None = None
    vehicle_year: str | None = None
    vehicle_bodytype: str | None = None
    vehicle_plateno: str | None = None
    vehicle_state: str | None = None
    vehicle_veh: str | None = None
    vehicle_estimateAmount: str | None = None
    vehicle_damage: str | None = None
    vehicle_whereCanBeSeen: str | None = None
    vehicle_WhenCanBeSeen: str | None = None
    vehicle_purposeOfUse: str | None = None
    vehicle_permission: str | None = None
    vehicle_driverLicenseNo: str | None = None
    vehicle_RelationToInsured: str | None = None
    vehicle_ownerSameAsInsured: str | None = None
    vehicle_driverSameAsOwner: str | None = None
    vehicle_ownerPhone1: str | None = None
    vehicle_ownerPhone1Home: str | None = None
    vehicle_ownerPhone1Bus: str | None = None
    vehicle_ownerPhone2: str | None = None
    vehicle_ownerPhone2Home: str | None = None
    vehicle_ownerPhone2Bus: str | None = None
    vehicle_ownerEmail1: str | None = None
    vehicle_ownerEmail2: str | None = None
    vehicle_driverPhone1: str | None = None
    vehicle_driverPhone1Home: str | None = None
    vehicle_driverPhone1Bus: str | None = None
    vehicle_driverPhone2: str | None = None
    vehicle_driverPhone2Home: str | None = None
    vehicle_driverPhone2Bus: str | None = None
    vehicle_driverEmail1: str | None = None
    vehicle_driverEmail2: str | None = None
    vehicle_dob: str | None = None
    vehicle_otherInsurance: str | None = None
    vehicle_otherPolicyNo: str | None = None
    vehicle_childSeatExists: str | None = None
    vehicle_childSeatInUse: str | None = None
    vehicle_childSeatLoss: str | None = None

    # Damaged Property / Other Party Vehicle Details
    damaged_owner: str | None = None
    damaged_make: str | None = None
    damaged_model: str | None = None
    damaged_year: str | None = None
    damaged_bodyType: str | None = None
    damaged_plateNo: str | None = None
    damaged_state: str | None = None
    damaged_VIN: str | None = None
    damaged_veh: str | None = None
    damaged_otherVeh: str | None = None
    damaged_non_vehicle: str | None = None
    damaged_damage: str | None = None
    damaged_otherDamageDescribe: str | None = None
    damaged_estimateAmount: str | None = None
    damaged_whereCanBeSeen: str | None = None
    damaged_vehicleCarrier: str | None = None
    damaged_vehiclePolicyNo: str | None = None
    damaged_vehicleNAIC: str | None = None
    damaged_driver: str | None = None
    damaged_driverSameAsOwner: str | None = None
    damaged_driverAddress: str | None = None
    damaged_ownerAddress: str | None = None
    damaged_ownerPhone1: str | None = None
    damaged_ownerPhone1Home: str | None = None
    damaged_ownerPhone1Bus: str | None = None
    damaged_ownerPhone2: str | None = None
    damaged_ownerPhone2Home: str | None = None
    damaged_ownerPhone2Bus: str | None = None
    damaged_ownerEmail1: str | None = None
    damaged_ownerEmail2: str | None = None
    damaged_driverPhone1Home: str | None = None
    damaged_driverPhone1Bus: str | None = None
    damaged_driverPhone2Home: str | None = None
    damaged_driverPhone2Bus: str | None = None
    damaged_driverEmail1: str | None = None
    damaged_driverEmail2: str | None = None

    # Injured Parties
    injured_name1: str | None = None
    injured_age1: str | None = None
    injured_phone1: str | None = None
    injured_address1: str | None = None
    injured_extent1: str | None = None
    injured_name2: str | None = None
    injured_age2: str | None = None
    injured_phone2: str | None = None
    injured_address2: str | None = None
    injured_extent2: str | None = None
    injured_name3: str | None = None
    injured_age3: str | None = None
    injured_phone3: str | None = None
    injured_address3: str | None = None
    injured_extent3: str | None = None
    injured_name4: str | None = None
    injured_age4: str | None = None
    injured_phone4: str | None = None
    injured_address4: str | None = None
    injured_extent4: str | None = None

    # Witness Details
    witness_name1: str | None = None
    witness_phone1: str | None = None
    witness_address1: str | None = None
    witness_name2: str | None = None
    witness_phone2: str | None = None
    witness_address2: str | None = None
    witness_name3: str | None = None
    witness_phone3: str | None = None
    witness_address3: str | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")

class ClaimUploadResponse(BaseModel):
    message: str
    claimId: int
    extractedFields: ExtractedFieldsSchema | Dict[str, Any]
    recommendedRoute: str | None
    reasoning: str | None
    claimRiskScore: int | None
    riskLevel: str | None
    claimStatus: str | None

    model_config = ConfigDict(from_attributes=True)
    
class ClaimResponse(BaseModel):
    id: int
    policy_number: str | None
    policyholder_name: str | None
    carrier: str | None
    estimated_damage: float | None
    recommended_route: str | None
    claim_status: str | None
    claim_risk_score: int | None
    risk_level: str | None
    raw_extracted_fields: Dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClaimListResponse(BaseModel):
    page: int
    size: int
    totalRecords: int
    totalPages: int
    claims: list[ClaimResponse]

    model_config=ConfigDict(from_attributes=True)
    
class UpdateClaimStatusRequest(BaseModel):
    claim_status: str

