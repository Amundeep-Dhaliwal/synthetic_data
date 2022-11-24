# synthetic_data
API that produces synthetic person data through the use of the Faker python package.

To run locally via docker:
```
$ make build
```

Minimal request:
```
{
  "number":1
}
```
Minimal response:
```
[
  {
    "name": "Sabrina Thomas",
    "email": "karenwilliams@hotmail.com",
    "gender": "F",
    "birthdate": "1981-03-17"
  }
]
```
By default the name, email, gender and birthdate fields are provided. The number of entries is recommended as < 10000 due to performance reasons.

Verbose request:
```
{
  "number":1,
  "age_lower_limit":20,
  "age_upper_limit":80,
  "fields": [
      "age",
      "deceased",
      "phone_number",
      "occupation",
      "address",
      "country",
      "nationality",
      "dependents"
    ]
}
```
Verbose response:
```
[
  {
    "name": "Caleb Melendez",
    "email": "hammondtara@yahoo.com",
    "gender": "M",
    "birthdate": "1970-11-24",
    "phone_number": "888.505.0561",
    "age": 52,
    "deceased": true,
    "address": "48900 Natalie Harbors Apt. 006\nWest Stephen, TN 20112",
    "nationality": "Tunisian",
    "country": "Tunisia",
    "occupation": "Geologist, wellsite",
    "dependents": [
      {
        "name": "Gregory Gonzalez",
        "email": "dstephens@hotmail.com",
        "gender": "M",
        "birthdate": "1919-09-03",
        "phone_number": "(141)073-0527x5237",
        "age": 103,
        "deceased": false,
        "address": "788 Emily Summit Suite 145\nAmandaborough, WA 60929",
        "nationality": "Surinamese",
        "country": "Suriname",
        "occupation": "Medical laboratory scientific officer"
      }
    ]
  }
]
```
### Age limits
#### `age_lower_limit`
Defaults to 0 if unspecified.
#### `age_upper_limit`
Specify upper limit of human age, limited to 120.

### Deceased
The older an individual, the higher the probability of truth.

### Phone number
Random phone number.

### Occupation
Random job title.

### Address
Random address.

### Country
Could be deduced from the address, otherwise random.

### Nationality
Could be related to the country, otherwise random.

### Dependents
A nested list of people whose age does not conform to the age range if specified.
