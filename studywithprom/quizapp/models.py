from django.db import models
from django.contrib.auth.admin import User
from datetime import datetime
from jsonfield import JSONField
from django.contrib.auth import get_user_model
User = get_user_model()
 
quizStyle = {'theme':'#b3ffb3', 'bgcolor':'#b3daff', 'head':'#ffccff'}

class Quiz(models.Model):
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.TextField(null=True)
    desc = models.TextField(null=True, default="")
    createDate = models.DateTimeField(auto_now_add=True)
    endDate = models.DateTimeField(blank=True, null=True, default=None)
    anonymous = models.BooleanField(default=True)
    style =  JSONField(null=True, default=quizStyle)
    access_code = models.TextField(null=True, default="openquiz")
 
class QuestionQ(models.Model):
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE)
    title = models.TextField()
    desc = models.TextField(null=True, default=None)
    qtype = models.IntegerField()
    order = models.IntegerField()
    pmarks = models.IntegerField(default=4)
    nmarks = models.IntegerField(default=0)
    answer = models.TextField(null=True, default='')

class OptionQ(models.Model):
    question = models.ForeignKey(QuestionQ, on_delete=models.CASCADE)
    value = models.TextField()
    isans = models.BooleanField(default=False)

class ResponseQ(models.Model):
    response_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    std_code = models.TextField(null=True, default='')
    access_code = models.TextField(null=True, default="showmeresult")

class PQresponseQ(models.Model):
    response = models.ForeignKey(ResponseQ, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionQ, on_delete=models.CASCADE)
    textans = models.TextField(null=True, default="")
    options =  JSONField(null=True, default={})