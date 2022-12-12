from copy import deepcopy
from pprint import pprint
from locust import HttpUser, task

# locust -f locust_testing.py --host http://localhost:8000 --users 5 --spawn-rate 5


class APIUser(HttpUser):
    request_body = {
        "number": 1000,
        "age_lower_limit": 10,
        "age_upper_limit": 100,
        "fields": ["name", "birthdate", "email", "gender", "age"],
    }

    @task
    def test_person_minimal(self):
        requested_fields = {}
        requested_fields["number"] = self.request_body["number"]
        self.client.get("/api/persons/", json=requested_fields)

    @task
    def test_person_verbose(self):
        self.client.get("/api/persons/", json=self.request_body)

    @task
    def test_person_verbose_with_dependents(self):
        request_body = deepcopy(self.request_body)
        request_body["fields"].append("dependents")
        self.client.get("/api/persons/", json=request_body)
