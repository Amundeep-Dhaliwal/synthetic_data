"""
This file contains mappings for the interchange of fields between
the user inputted fields and the faker profile field name.

It also lists the mandatory fields for 
a query and the possible query fields for the API
"""
OUTPUT_TO_INPUT_FIELD_MAPPING = {
    'sex':'gender',
    'mail':'email'
}

INPUT_TO_OUTPUT_FIELD_MAPPING = {value:key for key, value in OUTPUT_TO_INPUT_FIELD_MAPPING.items()}

MANDATORY_FIELDS = {
    'name', 
    'email',
    'gender', 
    'birthdate'
}

USER_QUERY_FIELDS = {
    'name', 
    'email', 
    'gender',
    'birthdate', 
    'age',
    'deceased',
    'phone',
    'address',
    'country', 
    'nationality',
    'occupation', 
    'dependents'
}