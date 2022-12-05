from django.test import TestCase
from django.test import AsyncClient

from unittest.mock import patch, Mock
from copy import copy, deepcopy
from asgiref.sync import async_to_sync
from pprint import pprint
import ujson
import numpy as np
from faker import Faker

from people.views import PersonAPIClass, RaisedResponse
from people.dataclass import Person, generate_persons
from people.fields import INPUT_TO_OUTPUT_FIELD_MAPPING

class PersonAPIClassTests(TestCase):
    content_tested_dict = {'content':'tested'}
    input_and_output_queries = (
            ['email', 'gender', 'birthdate', 'name'], 
            ['mail', 'sex', 'birthdate', 'name']
        )

    def setUp(self):
        self.client = AsyncClient()
        self.view = PersonAPIClass

    def assert_response(self, method, expected_status, *args):
        return_value = None
        try:
            return_value = method(self.view, *args)
        except RaisedResponse as response:
            self.assertEqual(response.status, expected_status)
            
        return return_value

    async def test_get(self):
        request_data = ujson.dumps({
            "number":1
        })

        with patch.object(self.view, 'process_get_request') as process:
            process.side_effect = RaisedResponse(self.content_tested_dict, 200)
            response = await self.client.generic('GET', '/api/persons/', request_data)
        
        formatted_content = ujson.dumps(self.content_tested_dict).encode('utf-8')
        
        self.assertEqual(response.content, formatted_content)
        self.assertEqual(response.status_code, 200)
    
    def test_raise_response(self):
        self.assert_response(
            self.view.raise_response, 200, self.content_tested_dict, 200
        )
    
    def test_get_number_of_people(self):
        number_specified = {'number':1}
        number_omitted = {}
        number = self.view.get_number_of_people(self.view, number_specified)
        self.assertEqual(number, 1)
        
        with patch.object(self.view, 'raise_response', side_effect = RaisedResponse(self.content_tested_dict, 412)) as raiser:
            self.assert_response(
                self.view.get_number_of_people, 412, number_omitted
            )

    def test_validate_input_fields(self):
        correct_field = ['name']
        validated_tuple = self.view.validate_inputted_fields(self.view, correct_field)
        self.assertEqual(validated_tuple[0], True)
        
        incorrect_field = ['nme']
        suggestion_tuple = self.view.validate_inputted_fields(self.view, incorrect_field)
        self.assertEqual(suggestion_tuple[2], 'name')

        incomprehensible_field = ['green']
        no_suggestion_tuple = self.view.validate_inputted_fields(self.view, incomprehensible_field)
        self.assertEqual(no_suggestion_tuple[0], False)
        self.assertEqual(no_suggestion_tuple[2], None)

    def test_process_get_request(self):
        valid_serializer = Mock()
        valid_serializer.is_valid.return_value = True
        invalid_serializer = Mock()
        invalid_serializer.is_valid.return_value = False
        with (
            patch.object(self.view, 'get_number_of_people', return_value = 1) as number,
            patch.object(self.view, 'handle_fields', return_value = deepcopy(self.input_and_output_queries)) as fields,
            patch.object(self.view, 'handle_age_restrictions',return_value =np.arange(10)) as array,
            patch.object(self.view, 'raise_response', side_effect =[RaisedResponse(self.content_tested_dict, 201), RaisedResponse(self.content_tested_dict, 500)]) as raiser,
            patch('people.views.PersonSerializer', side_effect = [valid_serializer,invalid_serializer]) as serializer
        ):
            self.assert_response(
                self.view.process_get_request, 201, self.content_tested_dict
            )

            fields.return_value = deepcopy(self.input_and_output_queries)

            self.assert_response(
                self.view.process_get_request, 500, self.content_tested_dict
            )
                                
    def test_handle_fields(self):
        fields = self.view.handle_fields(self.view, self.content_tested_dict)
        for tup in zip(fields, self.input_and_output_queries):
            self.assertEqual(*list(map(sorted,tup)))

        with (
            patch.object(self.view, 'raise_response', side_effect = RaisedResponse({}, 412)) as raiser,
            patch.object(self.view, 'validate_inputted_fields', side_effect = [(False, 0, 0), (True, 0,0), (True,0, 0)]) as validation
        ):
            incomplete_request_body = {
                'fields':['name']
            }
            self.assert_response(
                self.view.handle_fields, 412, incomplete_request_body
            )

            self.assert_response(
                self.view.handle_fields, 412, incomplete_request_body
            )           

            age_not_specified = {
                'age_lower_limit':5,
                'fields':['name','email','gender','birthdate']
            }
            
            self.assert_response(
                self.view.handle_fields, 412, age_not_specified
            )
    
    def test_handle_age_restrictions(self):
        no_age_limits = {}
        age_list = self.view.handle_age_restrictions(self.view, no_age_limits)
        self.assertEqual(age_list, None)

        only_upper = {'age_upper_limit': 15}
        array_from_zero = self.view.handle_age_restrictions(self.view,only_upper)
        self.assertEqual(isinstance(array_from_zero, np.ndarray), True)

        only_lower = {'age_lower_limit': 15}
        array_from_fifteen = self.view.handle_age_restrictions(self.view, only_lower)
        self.assertEqual(isinstance(array_from_fifteen, np.ndarray), True)

        lower_and_upper = {'age_lower_limit': 10, 'age_upper_limit':50}        
        half_open_array = self.view.handle_age_restrictions(self.view, lower_and_upper)
        self.assertEqual(len(half_open_array), 40)        

        with patch.object(self.view, 'raise_response', side_effect = RaisedResponse({}, 416)) as raiser:
            upper_limit_out_of_range = {'age_upper_limit': 150}
            self.assert_response(
                self.view.handle_age_restrictions, 416, upper_limit_out_of_range
            )

            lower_bigger_than_upper = {'age_lower_limit': 10, 'age_upper_limit':5}
            self.assert_response(
                self.view.handle_age_restrictions, 416, lower_bigger_than_upper
            )

class PersonDataClassTests(TestCase):
    fields = [
        'name',
        'email',
        'birthdate',
        'gender',

        'age',
        'deceased',
        'address',
        'phone',
        'occupation',
        'country',
        'nationality',
        'dependents'
    ]

    def setUp(self):
        Faker.seed(117)
        
    def test_person_generation(self):
        output_fields = []
        for field in self.fields:
            potential = INPUT_TO_OUTPUT_FIELD_MAPPING.get(field)
            if potential is None:
                potential = field
            output_fields.append(potential)
            
        person = generate_persons(1, self.fields, output_fields)

        student_fields = copy(self.fields)
        student_fields.remove('age')
        output_fields.remove('age')
        student_age_range= np.arange(16)
        no_age_specified_student = generate_persons(1, student_fields, output_fields, student_age_range)