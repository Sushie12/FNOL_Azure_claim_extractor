Project Title : AUTOMOBILE LOSS(FNOL-First Notice Of Loss) Document Analyser:-

OBJECTIVE/SUMMARY: 
Built an end-to-end intelligent claim processing system designed to automate First Notice of Loss (FNOL) document handling. The platform extracts unstructured data from uploaded claim PDFs and evaluates policy compliance, verifies estimate repair costs against live internet market pricing using an AI reasoning agent. Created a frontend interface to present actionable audit results on an interactive dashboard and restricted access(RBAC) to admin,reviewer and viewer. Data is stored in postgresql and containerized the appilcation on a light virtual box,Docker.

Breakdown: 
- MS Azure Document Intelligence extracts key fields from FNOL (First Notice of Loss) pdf documents.
- Identifies missing or inconsistent fields.
- Classifies the claim and routes it to the correct workflow. e.g: If anyone has been injured,then 'Specialist-Queue' route. 
- Client logs in as admin/reviewer/user on the frontend.
- Perform desired activity based on their respective authorized rights(Role based Access control)


DATA: Created dummy PDFs using the provided editable FNOL template(FNOL Template.pdf)

DEVELOPMENT ENVIRONMENT:
  - IDE: Visual Studio Code
  - Language: Python
  - Cloud Service: Microsoft Azure Document Intelligence, Docker
  - AI & LLM Frameworks: LangChain, Local LLM Inference (Ollama / vLLM using 12B parameter model)   
  - External APIs & Tools: SerpAPI (Live Web Search & Price Benchmarking)   
  - Authentication & Security: JWT (JSON Web Tokens) with Role-Based Access Control (RBAC)
  - Frontend Environment: Node.js, React.js (Vite / npm) 


Fields Extracted(14)-
  - "Policy Information": Policy No., PolicyHolder Name, PolicyHolder Email, Carrier,
  - "Incident Information": Date Of Loss, Time ,Location ,Estimated Damage ,Injured,
  - "Involved Parties": Agency, Contact Name, Contact Email,
  - "Asset Details": Vehicle Make, Vehicle Plate Number.

Data Validation-
  - Applied null-handling logic for empty values.
  - Set mandatory fields as:["Policy No", "Policyholder Name", "Carrier", "Estimate Amount"]
  - Implemented regex patterns for complex field extraction. Eg: Time field where AM,PM are checkboxed. InjuredName field comprising of multi-line text entries.
  - RBAC(Role-Based Access Control) is performed by allowing:
        Create claims, Delete claims, Change action to esclated/approved/rejected as many times, View Dashboard to ADMIN role ; 
            X        ,   X          , Change action to escalated/approved/rejected only once   , View Dashboard to REVIEWER role ;
            X        ,   X          ,      X                                                   , View Dashboard to VIEWER role.



Routing Logic-
   Applied routing rules strictly in the priority order-
    - I)If any mandatory field is missing- Manual Review.
    - II)If description contains 'inconsistent,'fraud','staged'- Investigation Flag.
    - III)If any person is injured- Specalist Queue.
    - IV)If estimate damage amount<25000 rupees - FastTrack.


Data Extraction Output for Pdf1.pdf:
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




