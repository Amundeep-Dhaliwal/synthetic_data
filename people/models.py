from django.db import models

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length = 100, null = False)
    mail = models.EmailField(max_length = 100, null = False)