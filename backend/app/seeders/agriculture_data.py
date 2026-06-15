agriculture_schemes = [

    {
        "scheme_name": "PM-KISAN",
        "scheme_code": "AGR001",

        "conditions": [

            {
                "field_name": "is_farmer",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a farmer",
            },

        ],

        "documents": [
            "Aadhaar Card",
            "Land Record",
            "Bank Passbook",
        ],
    },

    {
        "scheme_name": "Kisan Credit Card",
        "scheme_code": "AGR002",

        "conditions": [

            {
                "field_name": "is_farmer",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a farmer",
            },

        ],

        "documents": [
            "Aadhaar Card",
            "Land Record",
            "Income Proof",
            "Bank Passbook",
        ],
    },

    {
        "scheme_name": "Pradhan Mantri Fasal Bima Yojana",
        "scheme_code": "AGR003",

        "conditions": [

            {
                "field_name": "is_farmer",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a farmer",
            },

        ],

        "documents": [
            "Aadhaar Card",
            "Land Record",
            "Crop Details",
            "Bank Passbook",
        ],
    },

    {
        "scheme_name": "Soil Health Card Scheme",
        "scheme_code": "AGR004",

        "conditions": [

            {
                "field_name": "is_farmer",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a farmer",
            },

        ],

        "documents": [
            "Aadhaar Card",
            "Land Details",
        ],
    },

    {
        "scheme_name": "Agriculture Infrastructure Fund",
        "scheme_code": "AGR005",

        "conditions": [

            {
                "field_name": "is_farmer",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a farmer",
            },

        ],

        "documents": [
            "Aadhaar Card",
            "Land Record",
            "Project Proposal",
            "Bank Passbook",
        ],
    },

]