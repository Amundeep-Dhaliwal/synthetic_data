from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response

from django.contrib.auth.models import User
from pprint import pprint
import numpy as np

from people.serializers import PersonSerializer
from people.dataclass import generate_persons

class PersonAPIView(generics.ListCreateAPIView):

    def get(self, request, format = None):
        # Generate and raise custom exceptions when the request.data contains an invalid age range
        # return appropriate response codes (success, regex, invalid age)
        # incorrect field names require suggestions
        number_of_people = request.data['number']

        # Handle inputted fields
        inputted_fields = request.data.get('fields')
        requested_fields = inputted_fields if inputted_fields else []

        # Handle age restrictions
        age_list = None
        upper_age_limit = request.data.get('age_upper_limit')
        if upper_age_limit:
            lower_age_limit = request.data.get('age_lower_limit')
            
            if lower_age_limit > upper_age_limit:
                return Response(
                    {
                        'message':f'Please input a valid age range, as {lower_age_limit} > {upper_age_limit}'
                    }, 
                    status = status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            if lower_age_limit:
                age_list = np.arange(lower_age_limit, upper_age_limit)
            else:
                age_list = np.arange(upper_age_limit)
        
        generated_people = generate_persons(
            number = number_of_people,
            fields = requested_fields,
            age_list = age_list
        )

        serialized = PersonSerializer(data = generated_people, many = True)
        if serialized.is_valid():
            return Response(serialized.data, status = status.HTTP_201_CREATED)
        else:
            print(serialized.errors)
            return Response(serialized.data, status =status.HTTP_422_UNPROCESSABLE_ENTITY)
