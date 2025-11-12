agency_object = {
    "type": "object",
    "required": ["type", "tier", "name"],
    "properties": {
        "type": { "type": "string", "enum": ["awarding", "funding"] },
        "tier": { "type": "string", "enum": ["toptier", "subtier"] },
        "name": { "type": "string" },
        "toptier_name": {
            "type": "string",
            "description": (
                "Only applicable when tier is subtier. "
                "Ignored when tier is toptier. "
                "Provides a means by which to scope subtiers with "
                "common names to a specific toptier. "
                "For example, several agencies have an 'Office of Inspector General'. "
                "If not provided, subtiers may span more than on toptier."
            )
        }
    }
}

filter_object_award_types = {
    "type": "array",
    "default": ["A", "B", "C", "D"],
    "items": {
        "type": "string",
        "enum": [
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "A",
            "B",
            "C",
            "D",
            "IDV_A",
            "IDV_B",
            "IDV_B_A",
            "IDV_B_B",
            "IDV_B_C",
            "IDV_C",
            "IDV_D",
            "IDV_E",
        ],
    },
}

standard_location_object = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["country"],
        "properties": {
            "country": {
                "type": "string",
                "description": (
                    "A 3 character code indicating the country to search within. "
                    "If the country code is not USA, all further parameters can be ignored. "
                    "A special country code, FOREIGN, represents all non-US countries."
                )
            },
            "state": {
                "type": "string",
                "description": "A 2 character string abbreviation for the state or territory. ",
                "minLength": 2,
                "maxLength": 2,
            },
            "county": {
                "type": "string",
                "description": (
                    "A 3 digit FIPS code indicating the country. "
                    "If county is provided, a state must be provided as well. "
                    "If county is provided, a district_original must never be provided. "
                    "If county is provided, a district_current must never be provided."
                ),
                "minLength": 3,
                "maxLength": 3,
            },
            "city": {
                "type": "string",
                "description": (
                    "String city name. "
                    "If no state is provided, this will return results for all cities "
                    "in any state with the provided name."
                )
            },
            "district_original": {
                "type": "string",
                "description": (
                    "A 2 character code indicating the congressional district. "
                    "When provided, a state must be provided as well. "
                    "When provided, a county must never be provided. "
                    "When provided, a country must always be USA"
                    "When provided, district_current must never be provided."
                ),
                "minLength": 2,
                "maxLength": 2,
            },
            "district_current": {
                "type": "string",
                "description": (
                    "A 2 character code indicating the congressional district. "
                    "When provided, a state must be provided as well. "
                    "When provided, a county must never be provided. "
                    "When provided, a country must always be USA"
                    "When provided, district_original must never be provided."
                ),
                "minLength": 2,
                "maxLength": 2,
            },
            "zip": {
                "type": "string",
                "description": "A 5 digit string indicating the postal area to search within.",
                "minLength": 5,
                "maxLength": 5,
            }
        }
    }
}

time_period_object = {
    "type": "array",
    "items": {
        "anyOf": [
            {
                "type": "object",
                "title": "SubawardSearchTimePeriodObject",
                "required": ["start_date", "end_date"],
                "description": "Use this if spending_level is subawards or subawards is true",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": (
                            "Search based on one or more fiscal year selections OR date range. "
                            "Dates should be in the following format: YYYY-MM-DD"
                        ),
                    },
                    "end_date": {
                        "type": "string",
                        "description": (
                            "Search based on one or more fiscal year selections OR date range. "
                            "Dates should be in the following format: YYYY-MM-DD"
                        ),
                    },
                    "date_type": {
                        "type": "string",
                        "enum": ["action_date", "last_modified_date"],
                        "default": "action_date",
                    },
                },
            },
            {
                "type": "object",
                "title": "TransactionSearchTimePeriodObject",
                "required": ["start_date", "end_date"],
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": (
                            "Search based on one or more fiscal year selections OR date range. "
                            "Dates should be in the following format: YYYY-MM-DD"
                        ),
                    },
                    "end_date": {
                        "type": "string",
                        "description": (
                            "Search based on one or more fiscal year selections OR date range. "
                            "Dates should be in the following format: YYYY-MM-DD"
                        ),
                    },
                    "date_type": {
                        "type": "string",
                        "enum": [
                            "action_date",
                            "date_signed",
                            "last_modified_date",
                            "new_awards_only",
                        ],
                    },
                },
            },
        ]
    },
}

treasury_account_components = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["aid", "main"],
                "properties": {
                    "ata": {
                        "type": ["string", "null"],
                        "description": "Allocation Transfer Agency Identifier - three characters.",
                        "minLength": 3,
                        "maxLength": 3,
                    },
                    "aid": {
                        "type": "string",
                        "description": "Agency Identifier - three characters.",
                        "minLength": 3,
                        "maxLength": 3,
                    },
                    "bpoa": {
                        "type": ["string", "null"],
                        "description": "Beginning Period of Availability - four digits.",
                        "minLength": 4,
                        "maxLength": 4,
                    },
                    "epoa": {
                        "type": ["string", "null"],
                        "description": "Ending Period of Availability - four digits.",
                        "minLength": 4,
                        "maxLength": 4,
                    },
                    "a": {
                        "type": ["string", "null"],
                        "description": "Availability Type Code - X or null.",
                    },
                    "main": {
                        "type": "string",
                        "description": "Main Account Code - four digits.",
                        "minLength": 4,
                        "maxLength": 4,
                    },
                    "sub": {
                        "type": ["string", "null"],
                        "description": "Sub-Account Code - three digits.",
                        "minLength": 3,
                        "maxLength": 3,
                    }
                }
            }
        }

advanced_filter_object = {
    "type": "object",
    "properties": {
        "keywords": { "type": "array", "items": { "type": "string" }},
        "description": { "type": "string" },
        "time_period": time_period_object,
        "place_of_performance_scope": { "type": "string", "enum": [ "domestic", "foreign" ]},
        "agencies": agency_object,
        "recipient_search_text": {
            "type": "array", "items": { "type": "string" },
            "description": "Text searched across a recipient's name, UEI, and DUNS.",
            "minItems": 1 # Will return 422 if this is below min 1 items
        },
        "recipient_scope": { "type": "string", "enum": ["domestic", "foreign"] },
        "recipient_locations": standard_location_object,
        "recipient_type_names": { "type": "array", "items": { "type": "string" }},
        "award_type_codes": filter_object_award_types,
        'award_ids': {
            'type': 'array', 'items': { 'type': 'string', },
            'description': (
                "Award IDs surrounded by double quotes e.g \"SPE30018FLJFN\" "
                "will perform exact matches as opposed to the default, fuzzier full text matches. "
                "Useful for Award IDs that contain spaces or other word delimiters"
            )
        },
        'award_amounts': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'lower_bound': { 'type': 'number' },
                    'upper_bound': { 'type': 'number' },
                }
            }
        },
        "program_numbers": { "type": "array", "items": { "type": "string" }},
        "naics_codes": {
            "type": "object",
            "properties": {
                "require": { "type": "array", "items": { "type": "string" }},
                "exclude": { "type": "array", "items": { "type": "string" }},
            }
        },
        "tas_codes": {
            "type": "object",
            "properties": {
                "require": {
                    "type": "array",
                    "items": { "type": "array", "items": { "type": "string"} }
                },
                "exclude": {
                    "type": "array",
                    "items": { "type": "array", "items": { "type": "string"} }
                },
            }
        },
        "psc_codes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "require": {
                        "type": "array",
                        "items": { "type": "array", "items": { "type": "string"} }
                    },
                    "exclude": {
                        "type": "array",
                        "items": { "type": "array", "items": { "type": "string"} }
                    },
                }
            }
        },
        "contract_pricing_type_codes": { "type": "array", "items": { "type": "string" }},
        "set_aside_type_codes": { "type": "array", "items": { "type": "string" }},
        "extent_competed_type_codes" : { "type": "array", "items": { "type": "string" }},
        "treasury_account_components": treasury_account_components,
        "program_activity": { "type": "array", "items": { "type": "string" }},
        "program_activities": {
            "type": "object",
            "description": (
                "A filter option that supports filtering by a program activity name or code. "
                "If this is used at least name or code must be provided."
            ),
            "properties": {
                "name": { "type": "string" },
                "code": { "type": "string" },
            },
        },
    }
}
