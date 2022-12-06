from django.shortcuts import render
from django.views import View
from django.http.response import HttpResponse
from django.utils.decorators import classonlymethod

from rest_framework import status, generics
from rest_framework.response import Response
from asgiref.sync import sync_to_async

import os

import asyncio
from pprint import pprint
import numpy as np
import ujson
import enchant

from people.serializers import PersonSerializer
from people.dataclass import generate_persons
from people.fields import MANDATORY_FIELDS, USER_QUERY_FIELDS, INPUT_TO_OUTPUT_FIELD_MAPPING

dictionary = enchant.Dict('en_US')

class RaisedResponse(Exception):
    """An exception that is raised and propagates up the call stack

    Args:
        Exception : Contains human readable content and a HTTP status code
    """
    def __init__(self, content, status):
        self.content = content
        self.status = status

class PersonAPIClass(View):
    """A class based view that is responsible for the /api/persons/ endpoint

    Inherits from:
        View (Generic python class): Implements a dispatch-by-method and provides simple sanity checking
    """

    async def get(self, request, *args, **kwargs):
        """Handles GET requests asynchronously

        Args:
            request : request metadata

        Returns:
            HttpResponse: A response class with a content dictionary 
            and a HTTP status code
        """
        request_body = ujson.loads(request.body)
        try:
            self.process_get_request(request_body)
        except RaisedResponse as resp:
            return HttpResponse(
                content = ujson.dumps(resp.content),
                status = resp.status
            )
    
    def process_get_request(self, request_body):
        """Processes the request body, invokes the creation of data
        and returns the serialized response

        Args:
            request_body : request metadata
        
        Raises:
            RaisedResponse
        """
        number_of_people = self.get_number_of_people(request_body)

        input_query_fields, output_query_fields = self.handle_fields(request_body)

        age_list = self.handle_age_restrictions(request_body)

        if isinstance(age_list, np.ndarray):
            input_query_fields.remove('birthdate')
            output_query_fields.remove('birthdate')
        
        generated_people = generate_persons(
            number = number_of_people,
            input_fields = input_query_fields, # This list include email, gender
            output_fields = output_query_fields, # This list includes mail, sex
            age_list = age_list
        )

        serialized = PersonSerializer(data = generated_people, many = True)
        if serialized.is_valid():
            self.raise_response(
                serialized.data,
                status = status.HTTP_201_CREATED
            )
        
        self.raise_response(
            {
                'error':'An error was encountered whilst serializing the person data'
            },
            status =status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def raise_response(self, content, status):
        raise RaisedResponse(
            content = content,
            status = status
        )

    def get_number_of_people(self, request_body):
        number_of_people = request_body.get('number')
        if number_of_people is None:
            self.raise_response(
                {
                    "error":"Please specify the number of people that you desire"
                },
                status = status.HTTP_412_PRECONDITION_FAILED
            )

        return number_of_people
    
    def handle_fields(self,request_body):
        """Handles input validation and ensures mandatory 
        fields are provided and gives suggestions for mistyped fields

        Args:
            request_body : request metadata

        Returns:
            inputted_fields (list) : a list of the inputted fields as 
            specified in the request
            outputted_query_fields (list) : a list of fields that conform 
            to the faker specification
        """
        inputted_fields = request_body.get('fields')
        
        if inputted_fields:
            valid, inputted, suggestion = self.validate_inputted_fields(inputted_fields)
            if not valid:
                suggestion_string = f", perhaps you meant '{suggestion}'?" if suggestion else ""
                self.raise_response(
                    {
                        "error": f"{inputted} was not recognised as a valid field name{suggestion_string}"
                    },
                    status = status.HTTP_412_PRECONDITION_FAILED
                ) 
            
            if not MANDATORY_FIELDS.issubset(inputted_fields):
                self.raise_response(
                    {
                        "error": "Please specify name, email, gender and birthdate in the 'fields' array"
                    },
                    status = status.HTTP_412_PRECONDITION_FAILED
                )
            
            has_age_been_specified = bool(request_body.get('age_lower_limit') or request_body.get('age_upper_limit'))
            if has_age_been_specified and 'age' not in inputted_fields:
                self.raise_response(
                    {
                        "error":"Please request 'age' in the fields array as age limits have been explicitly provided"
                    },
                    status = status.HTTP_412_PRECONDITION_FAILED
                )
        else:
            inputted_fields = list(MANDATORY_FIELDS)

        output_query_fields = inputted_fields[:]
        for field in inputted_fields:
            if field in INPUT_TO_OUTPUT_FIELD_MAPPING.keys():
                index_position = inputted_fields.index(field)
                output_query_fields[index_position] = INPUT_TO_OUTPUT_FIELD_MAPPING[field]
        
        return inputted_fields, output_query_fields

    def handle_age_restrictions(self, request_body):
        """Handles validation of the provided age limits

        Args:
            request_body : request metadata

        Returns:
            age_list (None | np.ndarray): if age limits are not specified, 
            this method would return None. Else, a 1 dimensional array of potential integer ages.
        """
        age_list = None
        lower_age_limit = request_body.get('age_lower_limit')
        upper_age_limit = request_body.get('age_upper_limit')
        EXCLUSIVE_UPPER_AGE_LIMIT = 115

        if upper_age_limit is not None and upper_age_limit > EXCLUSIVE_UPPER_AGE_LIMIT:
            self.raise_response(
                {
                    'error':f'The upper age limit of {upper_age_limit} is not appropriate'
                }, 
                status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
            )

        if lower_age_limit or upper_age_limit:
            requested_fields = request_body.get('fields')
            if requested_fields is None:
                raise_exception = True
            else:
                raise_exception = 'age' not in requested_fields
            if raise_exception:
                self.raise_response(
                    {
                        'error':"Please specify 'age' in the fields array when providing age limits"
                    },
                    status=status.HTTP_412_PRECONDITION_FAILED
                )

        if lower_age_limit and upper_age_limit:
            if lower_age_limit >= upper_age_limit:
                self.raise_response(
                    {
                        'error':f'Please input a valid age range, as {lower_age_limit} is greater than or equal to {upper_age_limit}'
                    },
                    status = status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
                )

            age_list = np.arange(lower_age_limit, upper_age_limit)

        elif upper_age_limit:
            age_list = np.arange(upper_age_limit)
        
        elif lower_age_limit:
            age_list = np.arange(lower_age_limit, EXCLUSIVE_UPPER_AGE_LIMIT)
        
        return age_list


    def validate_inputted_fields(self, inputted_fields):
        """Suggests a field name for an erroneous inputted field

        Args:
            inputted_fields (list): user inputted fields

        Returns:
            3 element tuple: First element would correspond to whether the inputted fields are valid,
            second element would be the erroneous field and third would be a potential suggestion.
        """
        for field in inputted_fields:
            if field not in USER_QUERY_FIELDS:
                suggestions = dictionary.suggest(field)
                
                try:
                    string_suggestion = USER_QUERY_FIELDS.intersection(suggestions).pop()
                except KeyError:
                    return False, field, None
                
                return False, field, string_suggestion
        
        return True, None, None