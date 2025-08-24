# data_extractor/utils/taxonomy.py

SPECIALTY_TAXONOMY = {
    "Cardiology": [
        "cardiologist", "heart specialist", "interventional cardiology", 
        "cardiac surgery", "cardiothoracic", "heart failure"
    ],
    "Dermatology": [
        "dermatologist", "skin specialist", "cosmetic dermatologist", 
        "dermatopathologist", "trichologist", "venereologist"
    ],
    "Neurology": [
        "neurologist", "brain specialist", "nervous system", "epileptologist", 
        "neurophysiologist"
    ],
    "Oncology": [
        "oncologist", "cancer specialist", "medical oncologist", 
        "radiation oncologist", "surgical oncologist", "hemato-oncologist"
    ],
    "General Surgery": [
        "general surgeon", "laparoscopic surgeon", "trauma surgeon"
    ],
    "Orthopedics": [
        "orthopedist", "orthopaedic", "bone specialist", "joint specialist", 
        "spine surgeon", "sports medicine"
    ],
    "Neurosurgery": [
        "neurosurgeon", "brain surgeon", "spine surgeon"
    ],
    "Pediatrics": [
        "pediatrician", "child health", "neonatologist", 
        "pediatric subspecialist"
    ],
    "Obstetrics/Gynecology": [
        "obstetrician", "gynecologist", "gynaecologist", "women's health", 
        "fertility specialist", "maternal-fetal medicine", "ivf"
    ],
    "Psychiatry": [
        "psychiatrist", "mental health", "child psychiatrist", 
        "addiction specialist", "psychotherapist"
    ]
}

def classify_specialty(raw_specialty_string: str) -> str:
    """
    Identifies the primary specialty from a raw string based on keywords.
    Returns 'Uncategorized' if no match is found.
    """
    if not raw_specialty_string:
        return "Uncategorized"

    lower_spec = raw_specialty_string.lower()
    
    for primary_specialty, keywords in SPECIALTY_TAXONOMY.items():
        for keyword in keywords:
            if keyword in lower_spec:
                return primary_specialty
                
    return "Uncategorized"