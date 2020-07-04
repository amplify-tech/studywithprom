from django.http import JsonResponse
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import *
from datetime import datetime
import pytz
from random import randint
User = get_user_model()

tz = pytz.timezone('Asia/Kolkata')
import re 
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
# email regex

def check(email): 
	if(re.search(regex,email)): 
		return True	
	else: 
		return False

def home(request):
    if request.user.is_authenticated:
        return redirect('/survey/')
    else:
        all_users = User.objects.all()
        num = len(all_users)
        return render(request, 'home.html',{"numuser":num})

def team(request):
	return render(request, 'team.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email_login']
        paswd = request.POST['pswd_login']
        if len(email) <5 or len(email)>40:
            messages.info(request, 'Invalid Email')
            return redirect('/')
        elif len(paswd) <4 or len(paswd)>25:
            messages.info(request, 'Incorrect Password')
            return redirect('/')
        else:
	        user = auth.authenticate(email=email, password=paswd)

	        if user is not None:
	            auth.login(request,user)
	            return redirect('/survey/')
	        else:
	            messages.info(request, 'Invalid Email or Password')
	            return redirect('/')

    else:
        return render(request, '/')


def logout(request):
    user = request.user
    auth.logout(request)
    return redirect('/')


def register(request,  nvuser_id=None):
	myname = request.POST['myname']
	myemail = request.POST['myemail']
	mypswd1 = request.POST['mypswd1']
	mypswd2 = request.POST['mypswd2']

	msz=""
	valid=True
	if len(myname) <4 or len(myname)>25 :
		valid=False
		msz+="fullname should be 4-25 char long. "
	if len(mypswd1) <4 or len(mypswd1)>25 :
		valid=False
		msz+="password should be 4-25 char long. "
	if len(mypswd2) <4 or len(mypswd2)>25 :
		valid=False
		msz+="password should be 4-25 char long. "
	if mypswd2 != mypswd1:
		valid=False
		msz+="password not match. "
	if not check(myemail):
		valid=False
		msz+="Invalid email. "

	if User.objects.filter(email=myemail).exists():
		valid=False
		msz+="this email is already taken. "

	if(valid):
		new_user = User.objects.create_user(email=myemail,first_name=myname ,password=mypswd1)
		new_user.save()

		user = auth.authenticate(email=myemail, password=mypswd1)
		auth.login(request,user)

		newurl = '/survey/'

		response = {"status":"valid", "msz":msz, "url":newurl}

	else:
		response = {"status":"invalid", "msz":msz, "url":"/"}
	return JsonResponse(response, safe=False)