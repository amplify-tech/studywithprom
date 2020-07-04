from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
User = get_user_model()


def dashboard(request):
	return redirect("/")


def editprofile(request):
	if request.user.is_authenticated: 
		if request.method == 'POST':
			user=request.user
			fullname = request.POST['fullname']
			psswd = (request.POST['psswd']).strip()
			psswd2 = (request.POST['psswd2']).strip()
			if len(fullname)<3 or len(fullname)>25:
				messages.info(request, "fullname should be 3-25 char long. ")
				return render(request, 'editprof.html')
			else:
				user.first_name=fullname
				user.save()
			if len(psswd)>0 or len(psswd2)>0:  # user asked for password change
				if psswd2 != psswd:
					messages.info(request, 'password not match')
					return render(request, 'editprof.html')
				elif len(psswd) <4 or len(psswd)>25:
					messages.info(request, "password should be 4-25 char long. ")
					return render(request, 'editprof.html')
				else:
					user.set_password(psswd)
					user.save()
					messages.info(request, "password saved! login with new password")
			else:
				pass    #no need to change password

			# saved, user may need to login with new password.
			return redirect("/")

		else:
			return render(request, 'editprof.html')

	return redirect("/")
