from django.shortcuts import render
from .serializers import PersonSerializer
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.
from django.contrib.auth.models import User
from pprint import pprint

class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    queryset = User.objects.all()
    # def retrieve(self, request):
    #     raise ZeroDivisionError
    #     pprint(request)
    #     queryset = User.objects.all()
    #     serialized_object = self.serializer_class(queryset)
    #     return Response(serialized_object.data)
