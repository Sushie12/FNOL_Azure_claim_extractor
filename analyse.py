#Azure smart extraction only

import os
import json
import re
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from dotenv import load_dotenv # 1. Import the function

load_dotenv() # 2. Run the function to load your .env file

# 3. Now os.getenv will work!
endpoint = os.getenv("azure_endpoint")
key = os.getenv("azure_key")
client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))

def extract_to_json_format(file_path):
    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout",
            body=f,
            features=["queryFields"],
            query_fields=[
                "PolicyNumber", "InsuredName", "CarrierName", 
                "LossDate", "LossTime", "LossLocation", "EstimateAmount",
                "VehicleMake", "PlateNumber", "AgencyName", "ContactName",
                "CityStateZip", "InjuredName", "AccidentDescription", "DamageDescription",
                "InsuredEmail", "ContactEmail"
            ]
        )
    result = poller.result()

    # Extract paragraphs for location concatenation only
    paragraphs = [p.content for p in result.paragraphs]
    full_text = "\n".join(paragraphs)
    
    # Map AI Query results (Smart Extraction)
    smart_results = {}
    if result.documents:
        for name, field in result.documents[0].fields.items():
            val = field.value_string if hasattr(field, 'value_string') else field.content
            smart_results[name] = val.strip() if val else None

    # Helper to get smart field with default
    def get_smart(key):
        return smart_results.get(key)

    # Data Extraction - 100% Azure Smart Extraction
    all_extracted_data = {
        "Policy No": (lambda x: x if x and any(c.isdigit() for c in x) else "null")(
            get_smart("PolicyNumber")
        ),
        
        "Policyholder Name": (lambda x: x.strip() if x and len(x.strip()) > 2 and not x.isupper() else "null")(
            get_smart("InsuredName")
        ),
        
        "Carrier": (lambda x: x.strip() if x and "CARRIER" not in x.upper() else "null")(
            get_smart("CarrierName")
        ),
        "Insured Email": (lambda x: x.strip() if x and "@" in x else "null")(
            get_smart("InsuredEmail")
        ),

        "Contact Email": (lambda x: x.strip() if x and "@" in x else "null")(
            get_smart("ContactEmail")
        ),
        
        "Date of Loss": (lambda x: 
            x.strip() if x and 
            not any(label in x.upper() for label in ["AM", "PM", "DATE"]) 
            and any(c.isdigit() for c in x) 
            else "null"
        )(get_smart("LossDate")),
        
        "Time": (lambda x: 
            (
                # 1. Extract just the numbers/colon (e.g., "08:36")
                re.sub(r'[^0-9:]', '', x).strip() + 
                # 2. Strict PM Check: Only if tick/X is directly near "PM"
                (
                    " PM" if re.search(r'[\u2713\u2714☑xX]\s*PM', x, re.IGNORECASE) 
                    else " AM"
                )
            ) if x and any(c.isdigit() for c in x) else "null"
        )(get_smart("LossTime")),
        
        "Location": (lambda street, city: f"{street}, {city}" if street and city and not "STREET" in street.upper() else "null")(
            get_smart("LossLocation"),
            get_smart("CityStateZip")
        ),
        
        "Estimate Amount": (lambda x: x if x and any(c.isdigit() for c in x) else "null")(
            get_smart("EstimateAmount")
        ),
        
        "Make": (lambda x: x.strip() if x and "MAKE" not in x.upper() else "null")(
            get_smart("VehicleMake")
        ),
        
        "Plate Number": (lambda x: x.strip() if x and any(c.isdigit() for c in x) else "null")(
            get_smart("PlateNumber")
        ),
        
        "Contact Name": (lambda x: x.strip() if x and not x.isupper() and "CONTACT" not in x.upper() else "null")(
            get_smart("ContactName")
        ),
        
        "Agency": (lambda x: x.strip() if x and "AGENCY" not in x.upper() and len(x.strip()) > 2 else "null")(
            get_smart("AgencyName")
        ),
        
        "Injured": (lambda x: 
            x.split('\n')[0].strip() if x and 
            not any(label in x.upper() for label in ["NAME & ADDRESS", "PHONE", "INJURED"]) 
            and len(x.strip()) > 2 
            else "null"
        )(get_smart("InjuredName"))
    }

    # Analyst Logic
    mandatory = ["Policy No", "Policyholder Name", "Carrier", "Estimate Amount"]
    missing = [f for f in mandatory if all_extracted_data.get(f) in [None, "null", ""]]
    
    # Investigation Flag Logic - Using Smart Extraction
    accident_text = get_smart("AccidentDescription") or ""
    damage_text = get_smart("DamageDescription") or ""
    
    risk_keywords = ["inconsistent", "fraud", "staged"]
    combined_text = (accident_text + " " + damage_text).lower()
    found_words = [word for word in risk_keywords if word in combined_text]
    investigation_flag = bool(found_words)
    
    # Convert estimate to numeric
    string_num = all_extracted_data.get('Estimate Amount')
    if string_num and string_num != "null":
        # Remove commas and convert to float
        numeric_estimate = float(str(string_num).replace(',', '').strip())
    else:
        numeric_estimate = 0

    if missing:
        route = "Manual Review"
        reason = f"Missing fields: {', '.join(missing)}"
    elif numeric_estimate < 25000:
        route = "Fast-Track"
        reason = f"Estimate Amount- Rs.{all_extracted_data['Estimate Amount']}, is less than Rs.25,000."
    elif investigation_flag:
        route = "Investigation Flag"
        reason = f"Risk keywords found- {', '.join(found_words)}"
    elif all_extracted_data["Injured"]!="null":
        route = "Specialist Queue"
        reason = f"Injured person name-{all_extracted_data['Injured']}. So claim type is 'Injury'"

    return {
        "extractedFields": {
            "Policy Information": {
                "Policy No.": all_extracted_data["Policy No"],
                "PolicyHolder Name": all_extracted_data["Policyholder Name"],
                "PolicyHolder Email":all_extracted_data["Insured Email"],
                "Carrier": all_extracted_data["Carrier"]
            },
            "Incident Information": {
                "Date Of Loss": all_extracted_data["Date of Loss"],
                "Time": all_extracted_data["Time"],
                "Location": all_extracted_data["Location"],
                "Estimated Damage": all_extracted_data["Estimate Amount"],
                "Injured": all_extracted_data["Injured"]
            },
            "Involved Parties": {
                "Agency": all_extracted_data["Agency"],
                "Contact Name": all_extracted_data["Contact Name"],
                "Contact Email":all_extracted_data["Contact Email"]
            },
            "Asset Details": {
                "Vehicle Make": all_extracted_data["Make"],
                "Vehicle Plate Number": all_extracted_data["Plate Number"]
            }
        },
        "missingFields":[f"{len(missing)} MISSING VALUE(S)-{m.upper()},out of 4 mandatory fields-{mandatory}" for m in missing] if missing else [f" No Missing values out of mandatory fields-{mandatory}"],
        "recommendedRoute": route,
        "reasoning": reason
    }

# 2. BATCH PROCESSING
folder_path = "pdfs" 
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):
        try:
            output = extract_to_json_format(os.path.join(folder_path, filename))
            print(f"\n-------------Result for: {filename}--------------")
            print(json.dumps(output, indent=4))
        except Exception as e:
            print(f"FAILED {filename}: {e}")