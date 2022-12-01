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