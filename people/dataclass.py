import os
import csv
from dataclasses import dataclass, field, asdict
from pprint import pprint
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.conf import settings
from faker import Faker
import pycountry
import numpy as np

from people.fields import (
    MANDATORY_FIELDS,
    OUTPUT_TO_INPUT_FIELD_MAPPING,
    INPUT_TO_OUTPUT_FIELD_MAPPING,
)

csv_path = os.path.join(settings.BASE_DIR, "demonyms.csv")
with open(csv_path, "r") as f:
    contents = csv.reader(f)
    nationalities = {x[1]: x[0] for x in contents}
list_nationalities = list(nationalities.values())

generator = Faker()


@dataclass
class Person:
    """
    A dataclass that represents a person, attributes and helper methods are specified
    """

    skeleton: dict = field(init=True)
    fields: list = field(init=True)

    name: str = field(default=None)
    email: str = field(default=None)
    birthdate: date = field(default=None)

    gender: str = field(default=None)
    age: int = field(default=None)
    deceased: bool = field(default=None)

    address: str = field(init=False, default=None)
    phone: str = field(init=False, default=None)
    occupation: str = field(init=False, default=None)

    country: str = field(init=False, default=None)
    nationality: str = field(init=False, default=None)

    dependents: list = field(default=None)

    def __post_init__(self):
        """
        Invoked after dataclass initialization, iterates over the dictionary of attributes
        specified for this instance and ensures they are initialized through the use of
        the helper methods
        """
        for key, value in self.skeleton.items():
            attribute_name = OUTPUT_TO_INPUT_FIELD_MAPPING.get(key)
            if attribute_name is None:
                attribute_name = key
            setattr(self, attribute_name, value)

        for attr in self.fields:
            if not getattr(self, attr):
                try:
                    getattr(self, f"create_{attr}")()
                except AttributeError as exception:
                    print(
                        f"\nAttempted to set attribute {attr}\nException:\n{exception}\n"
                    )

        self.skeleton = None
        self.fields = None

    def create_age(self) -> None:
        """
        Creates the age attribute by accounting for birthdate of this instance
        """
        today = date.today()
        self.age = (
            today.year
            - self.birthdate.year
            - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        )

    def create_deceased(self):
        """
        Human age in the context of of this API is constrained to 0 <= 𝑥 <= 120
        Evaluating the sin((π/240)*𝑥) gives the probability of an individual being deceased
        """
        if not getattr(self, "age"):
            self.create_age()
        probability_deceased = np.sin((np.pi / 240) * self.age)
        self.deceased = np.random.choice(
            [True, False], p=[probability_deceased, 1 - probability_deceased]
        )

    def create_phone(self) -> None:
        """
        Randomly generates a string phone number
        """
        self.phone = generator.phone_number()

    def create_occupation(self) -> None:
        """
        Creates a occupation based on this instances age
        """
        if not getattr(self, "age"):
            self.create_age()
        occupation = generator.job()
        if self.age < 16:
            occupation = "Student"
        elif self.age < 24:
            occupation = np.random.choice(["Student", occupation], p=[0.7, 0.3])
        self.occupation = occupation

    def create_country(self) -> None:
        """
        If this instance has an address attribute, use the two letter code
        to deduce the country else generate the country randomly
        """
        country_data = None
        if getattr(self, "address"):
            two_letter_code = self.address.split()[-2]
            country_data = pycountry.countries.get(alpha_2=two_letter_code)
        self.country = country_data.name if country_data else generator.country()

    def create_nationality(self) -> None:
        """
        Assign this attributes nationality to either the country of residence or randomly
        """
        if not getattr(self, "country"):
            self.create_country()
        country_nationality = nationalities[self.country]
        random_nationality = np.random.choice(list_nationalities)
        self.nationality = np.random.choice(
            [country_nationality, random_nationality], p=[0.7, 0.3]
        )

    def create_dependents(self) -> None:
        """
        Upon invocation a random number of people are assigned as dependents of this instance
        """
        number_of_dependents = np.random.choice(np.arange(4))
        copy_fields = list(self.fields)
        copy_fields.remove("dependents")
        if "birthdate" not in copy_fields:
            copy_fields.append("birthdate")
        if getattr(self, "age") and "age" not in copy_fields:
            copy_fields.append("age")

        output_fields = []
        for field in copy_fields:
            potential = field
            if field in INPUT_TO_OUTPUT_FIELD_MAPPING.keys():
                potential = INPUT_TO_OUTPUT_FIELD_MAPPING[field]
            output_fields.append(potential)

        self.dependents = generate_persons(
            number_of_dependents, copy_fields, output_fields
        )


def generate_persons(
    number: int,
    input_fields: list[str],
    output_fields: list[str],
    age_list: list[int] = None,
) -> list[dict]:
    """Creates a list of synthetic person entries

    Args:
        number (int): The number of entries generated
        input_fields (list[str]): A list of desired fields as specified by the user input
        output_fields (list[str]): A list of desired fields conforming to the faker specification
        age_list (list[int], optional): A numpy 1 dimensional array outlining the potential age range as specified by the user. Defaults to None.

    Returns:
        list[dict]: a list of generated data
    """
    people = []
    dictionary_factory = lambda x: {k: v for (k, v) in x if v is not None}
    for i in range(number):
        skeleton = generator.profile(fields=output_fields)

        if isinstance(age_list, np.ndarray):
            age = np.random.choice(age_list)
            skeleton["age"] = age
            skeleton["birthdate"] = date.today() - relativedelta(years=age)

        person = Person(skeleton=skeleton, fields=input_fields)

        people.append(asdict(person, dict_factory=dictionary_factory))

    return people
