# synthetic_data
API that produces synthetic person data through the use of the Faker python package.

## Prequisites

Python 3.9 or higher (user `python --version` to find out)
enchant (see [Installation](#installation) section)
All the packages mentioned in the `requirements.txt` (see [Installation](#installation) section)

## Installation

_Linux_
```bash
[sudo] apt-get update
[sudo] apt-get install enchant
```

_macOS_
```bash
brew install enchant
```

Once the above have been successfully installed, please do the below:

```bash
pip install --user -r requirements.txt
```

## Running
To run locally via docker:
```
$ make build
```

To run tests
```
$ make test
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
By default the name, email, gender and birthdate fields are provided. The number of entries is recommended as < 10000 due to performance.

Verbose request:
```
{
  "number":1,
  "age_lower_limit":20,
  "age_upper_limit":80,
  "fields": [
      "name",
      "email",
      "gender",
      "birthdate",
      "age",
      "deceased",
      "phone",
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
You are required to enter the fields name, email, birthdate and gender into the fields array. Mistyped fields can have helpful suggestions.
### Age limits
If age limits are specified, then age would be required in the requested fields.
#### `age_lower_limit`
Defaults to 0 if unspecified.
#### `age_upper_limit`
Specify upper limit of human age, limited to 115.

### Deceased
The older an individual, the higher the probability of truth.

### Phone
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
