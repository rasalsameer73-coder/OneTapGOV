education_schemes = [

    {
        "scheme_name": "Post Matric Scholarship",
        "scheme_code": "EDU001",

        "conditions": [

            {
                "field_name": "is_student",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a student",
            },

            {
                "field_name": "annual_income",
                "comparison_operator": "<=",
                "comparison_value": "250000",
                "human_readable_condition":
                    "Annual family income should not exceed ₹2.5 lakh",
            },
        ],

        "documents": [
            "Aadhaar Card",
            "Income Certificate",
            "Bonafide Certificate",
            "Previous Marksheet",
            "Bank Passbook",
        ],
    },

    {
        "scheme_name": "AICTE Pragati Scholarship",
        "scheme_code": "EDU002",

        "conditions": [

            {
                "field_name": "is_student",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a student",
            },

            {
                "field_name": "is_woman",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a female student",
            },

            {
                "field_name": "annual_income",
                "comparison_operator": "<=",
                "comparison_value": "800000",
                "human_readable_condition":
                    "Annual family income should not exceed ₹8 lakh",
            },
        ],

        "documents": [
            "Aadhaar Card",
            "Income Certificate",
            "Admission Letter",
            "Fee Receipt",
            "Bank Passbook",
        ],
    },

    {
        "scheme_name": "Central Sector Scholarship",
        "scheme_code": "EDU003",

        "conditions": [

            {
                "field_name": "is_student",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a student",
            },

            {
                "field_name": "percentage",
                "comparison_operator": ">=",
                "comparison_value": "80",
                "human_readable_condition":
                    "Student must have scored at least 80%",
            },
        ],

        "documents": [
            "Aadhaar Card",
            "Previous Marksheet",
            "Bonafide Certificate",
            "Bank Passbook",
        ],
    },

    {
        "scheme_name": "INSPIRE Scholarship",
        "scheme_code": "EDU004",

        "conditions": [

            {
                "field_name": "is_student",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a student",
            },

            {
                "field_name": "percentage",
                "comparison_operator": ">=",
                "comparison_value": "85",
                "human_readable_condition":
                    "Student must have scored at least 85%",
            },
        ],

        "documents": [
            "Aadhaar Card",
            "Previous Marksheet",
            "Admission Letter",
        ],
    },

    {
        "scheme_name": "NSP Merit Scholarship",
        "scheme_code": "EDU005",

        "conditions": [

            {
                "field_name": "is_student",
                "comparison_operator": "==",
                "comparison_value": "true",
                "human_readable_condition":
                    "Applicant must be a student",
            },

            {
                "field_name": "annual_income",
                "comparison_operator": "<=",
                "comparison_value": "600000",
                "human_readable_condition":
                    "Annual family income should not exceed ₹6 lakh",
            },
        ],

        "documents": [
            "Aadhaar Card",
            "Income Certificate",
            "Previous Marksheet",
        ],
    },

]