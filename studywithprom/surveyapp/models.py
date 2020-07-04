from django.db import models
from django.contrib.auth.admin import User
from datetime import datetime
from jsonfield import JSONField
from django.contrib.auth import get_user_model
User = get_user_model()

surveyStyle = {'theme':'#b3ffb3', 'bgcolor':'#b3daff', 'head':'#ffccff'}

class Survey(models.Model):
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.TextField(null=True)
    desc = models.TextField(null=True, default="")
    createDate = models.DateTimeField(auto_now_add=True)
    endDate = models.DateTimeField(blank=True, null=True, default=None)
    anonymous = models.BooleanField(default=True)
    style =  JSONField(null=True, default=surveyStyle)
    access_code = models.TextField(null=True, default="opensurvey")

class Question(models.Model):
    survey = models.ForeignKey(Survey,on_delete=models.CASCADE)
    title = models.TextField()
    desc = models.TextField(null=True, default=None)
    qtype = models.IntegerField()
    order = models.IntegerField()
    required = models.BooleanField()
    other = models.BooleanField()
    constraint =  JSONField(null=True, default={})

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.TextField()

class Response(models.Model):
    response_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

class PQresponse(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    textans = models.TextField(null=True, default="")
    options =  JSONField(null=True, default={})