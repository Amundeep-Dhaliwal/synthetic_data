from rest_framework import serializers
from django.contrib.auth.models import User
from people.models import Person


class BaseSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True, max_length=100)
    gender = serializers.ChoiceField(required=True, choices=["M", "F"])
    birthdate = serializers.DateField(required=True)
    phone = serializers.CharField(required=False, max_length=100)
    age = serializers.IntegerField(required=False)
    deceased = serializers.BooleanField(required=False)
    address = serializers.CharField(required=False, max_length=100)
    nationality = serializers.CharField(required=False, max_length=100)
    country = serializers.CharField(required=False, max_length=100)
    occupation = serializers.CharField(required=False, max_length=100)


class DependentSerializer(BaseSerializer):
    pass


class PersonSerializer(BaseSerializer):
    dependents = DependentSerializer(required=False, many=True)
