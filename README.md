AUTOMOBILE LOSS(FNOL) Documents Analyser:-

OBJECTIVE: Build a lightweight agent that,
- Extracts key fields from FNOL (First Notice of Loss) documents.
- Identifies missing or inconsistent fields.
- Classifies the claim and routes it to the correct workflow.

DATA: Created 4 dummy PDFs using the provided editable FNOL template.

DEVELOPMENT ENVIRONMENT:
  - IDE: Visual Studio Code
  - Language: Python
  - Cloud Service: Microsoft Azure Document Intelligence
  - Authentication: Azure Endpoint and API Key

WORKING:

Azure Integration-Connected Visual Studio Code to Azure Document Intelligence using endpoint and API key credentials for document processing.

Fields Extracted(14)-
  - "Policy Information": Policy No., PolicyHolder Name, PolicyHolder Email, Carrier,
  - "Incident Information": Date Of Loss, Time ,Location ,Estimated Damage ,Injured,
  - "Involved Parties": Agency, Contact Name, Contact Email,
  - "Asset Details": Vehicle Make, Vehicle Plate Number.

Data Validation-
  - Applied null-handling logic for empty values.
  - Set mandatory fields as:["Policy No", "Policyholder Name", "Carrier", "Estimate Amount"]
  - Implemented regex patterns for complex field extraction. Eg: Time field where AM,PM are checkboxed. InjuredName field comprising of multi-line text entries.

Routing Logic-
   Applied routing rules strictly in the priority order-
    - I. If any mandatory field is missing- Manual Review.
    - II. If estimate damage<25000- FastTrack.
    - III. If description contains 'inconsistent,'fraud','staged'- Investigation Flag.
    - IV. If any person is injured- Specalist Queue.


OUTPUT FOR Pdf1.pdf:
-------------Result for: pdf1.pdf--------------
{
    "extractedFields": {
        "Policy Information": {
            "Policy No.": "POL-85412",
            "PolicyHolder Name": "Jane Anderson Doe",
            "PolicyHolder Email": "jane@gmail.com",
            "Carrier": "Policy Bazaar"
        },
        "Incident Information": {
            "Date Of Loss": "12/05/2021",
            "Time": "08:36 AM",
            "Location": "CMR complex, Mumbai, Maharashtra",
            "Estimated Damage": "12000",
            "Injured": "null"
        },
        "Involved Parties": {
            "Agency": "null",
            "Contact Name": "Rick Doe",
            "Contact Email": "rick@gmail.com"
        },
        "Asset Details": {
            "Vehicle Make": "Suzuki",
            "Vehicle Plate Number": "MHCK-8521"
        }
    },
    "missingFields": [
        " No Missing values out of mandatory fields-['Policy No', 'Policyholder Name', 'Carrier', 'Estimate Amount']"
    ],
    "recommendedRoute": "Fast-Track",
    "reasoning": "Estimate Amount- Rs.12000, is less than Rs.25,000."
}




