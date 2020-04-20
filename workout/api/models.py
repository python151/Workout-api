from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Muscel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=350)

class Exercise(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=350)
    type = models.CharField(max_length=500)
    muscelOrMuscelGroup = models.ManyToManyField(Muscel)

class Set(Exercise):
    amountOfExercise = models.SmallIntegerField()

class Workout(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ManyToManyField(User)
    sets = models.ManyToManyField(Set)
    