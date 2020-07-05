import json
from django.http import JsonResponse
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth import get_user_model

# import datetime
from django.conf import settings
from django.utils.timezone import make_aware
 
from django.utils import timezone
from .models import *
import re, csv
from datetime import datetime
import pytz
import string   
import random
User = get_user_model()

utc=pytz.UTC

qtyparr =['Short Ans', 'Paragraph', 'Multiple choice', 
			'Checkboxes', 'Drop-down', 'linear scale', 
			'Date', 'Time']

def hash_int(n):
    mapping = list(range(48,48+10)) + list(range(97,97+26))
    h = str(hash(str(n)))[1:]  # values range from 0 to 9
    random.seed(n)
    str_h = "".join([ chr(mapping[int(x)+random.randint(0,26)]) for x in h ])
    random.seed()
    return str_h


def dashboard(request) :
    if request.user.is_authenticated: 
        user = request.user
        allsurv = Survey.objects.filter(owner=user).order_by("-id").values("id","title","createDate", 'access_code')
        return render(request, 'survey/dashboard.html', {"allsurv":allsurv}) 

    return redirect("/")


def gotosrv(request, sur_id=None):
	# return response(request,sur_id)
	return redirect("/survey/response/" + str(sur_id))
	# this is extra, in case user enter this type of url (/surevy/<id>) 
	# he will be redirected to response page


def newsurvey(request) :
	if request.user.is_authenticated: 
		user = request.user
		numsrv = Survey.objects.filter(owner=user).count()
		title = "New Survey - " + str(numsrv+1)
		new_survey = Survey(owner=user, title=title,endDate=None )
		new_survey.save()
		new_survey.access_code = hash_int(new_survey.id)
		new_survey.save()

		qtitle = "write your question here"
		newQ = Question(survey=new_survey, title=qtitle, qtype=0,
			order=99, required=False, other=False)
		newQ.save()

		return redirect("/survey/editor/" + str(new_survey.id)) 

	return redirect("/")

def editor(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			thesurvey = Survey.objects.get(id=int(sur_id), owner=user)
			all_itsQ = Question.objects.filter(survey=thesurvey).order_by('order','id')

			qdict = {}
			for Q in all_itsQ:
				optlist = Option.objects.filter(question=Q).order_by('id')
				qdict[Q]= optlist

			sharinglink = 'https://studywithprom.pythonanywhere.com/survey/viewform/' + str(thesurvey.access_code)

			context={'survey':thesurvey, 'Qdict':qdict,
					  'qtyparr':qtyparr, 'sharinglink':sharinglink}
			return render(request, 'survey/editor.html', context) 

	return redirect("/")

def orderq(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			thesurvey = Survey.objects.get(id=int(sur_id), owner=user)
			all_itsQ = Question.objects.filter(survey=thesurvey).order_by('order', 'id')
			context = {'thesurvey':thesurvey, 'all_itsQ':all_itsQ}

			return render(request, 'survey/orderq.html', context) 

	return redirect("/")


def modifysurvey(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			form_title = request.POST['form_title']
			form_desc = request.POST['form_desc']
			form_exdate = request.POST['form_exdate']

			# print(form_exdate)

			thesurvey = Survey.objects.get(id=int(sur_id), owner=user)

			#  update the survey part like title,date
			thesurvey.title = form_title
			thesurvey.desc = form_desc
			try:
				thesurvey.endDate = datetime.strptime(form_exdate, "%Y-%m-%dT%H:%M")
			except:
				thesurvey.endDate = None
				# print(e, "some problem in savning date")

			thesurvey.save()

			return HttpResponse("success")
	return redirect("/")

def addoneq(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			thesurvey = Survey.objects.get(id=int(sur_id), owner=user)
			qtitle = "write your question here"
			newQ = Question(survey=thesurvey, title=qtitle, qtype=0,
				order=99, required=False, other=False)
			newQ.save()
			# print(newQ.id , " new q created")

			response = {"id": int(newQ.id)}
			return JsonResponse(response, safe=False)

	return redirect("/")

def copyoneq(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			oldqid=request.POST['oldqid']

			isitmyQ = Question.objects.filter(id=int(oldqid), survey__owner=user)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			theoldq_foruse = isitmyQ[0]
			theoldq = Question.objects.get(id=int(oldqid), survey__owner=user)
			theoldq.id=None
			theoldq.save()          #now this will work as new Q
			# print(theoldq.id," Q clone succeful with id ")

			optidlist = []
			if theoldq.qtype>=2 and theoldq.qtype<=4:
				alloldopt = Option.objects.filter(question=theoldq_foruse).order_by("id")
				for opt in alloldopt:
					# print(opt.id, " old opt id")
					newopt = Option(question=theoldq, value=opt.value)
					newopt.save()
					# print(newopt.id, " new opt id")

					optidlist.append(newopt.id)
			
			# print("optidlist = ",optidlist)


			response = {"id": int(theoldq.id), "optidlist":optidlist}
			return JsonResponse(response, safe=False)

	return redirect("/")

def addoneopt(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			qid = request.POST['qid']
			optval = request.POST['optval']

			isitmyQ = Question.objects.filter(id=int(qid), survey__owner=user)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			theQ = isitmyQ[0]
			newOpt = Option(question=theQ,value=optval)
			newOpt.save()

			response = {"id": int(newOpt.id)}
			# print(newOpt.id, " new opt added")
			# print(newOpt.value, " new opt added")
			return JsonResponse(response, safe=False)

	return redirect("/")

def removeoneq(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			qid = request.POST['qid']

			isitmyQ = Question.objects.filter(id=int(qid), survey__owner=user)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			isitmyQ.delete()
			# print(qid, " Q removed")
			return HttpResponse("success")

	return redirect("/")

def removeoneopt(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			optid = request.POST['optid']

			isitmyOpt = Option.objects.filter(id=int(optid), question__survey__owner=user)
			if isitmyOpt.count()==0:
				return HttpResponse("access denied")

			isitmyOpt.delete()
			# print(optid, " option removed")
			return HttpResponse("success")

	return redirect("/")


def modifyoneq(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			type_of_change = request.POST['type']
			qid = request.POST['qid']

			isitmyQ = Question.objects.filter(id=int(qid), survey__owner=user)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			theQ = isitmyQ[0]

			optid_response = -1

			if type_of_change=='qtitle_changed':
				qtitle = request.POST['qtitle']
				theQ.title = qtitle
				# print(qtitle)

			elif type_of_change=='qtype_changed':
				newqtype = int(request.POST['qtype'])
				oldqtype = theQ.qtype
				# print(oldqtype, "oldqtype")
				theQ.qtype = newqtype
				if (oldqtype >=2 and oldqtype <=4) and (newqtype <2 or newqtype >4):
					Option.objects.filter(question=theQ).delete()
					# print("phle option the, ab nhi he, so del all opt")
				
				elif (oldqtype <2 or oldqtype >4) and (newqtype >=2 and newqtype <=4):
					optval = "option-1"
					newOpt = Option(question=theQ,value=optval)
					newOpt.save()
					optid_response=newOpt.id

					# print("phle option nhi the, ab he, so create only one new opt")

				# print(newqtype)

			elif type_of_change=='isreq_changed':
				isreq = request.POST['isreq']
				if isreq=='true':
					theQ.required = True
				else:
					theQ.required = False
				# print(isreq)

			elif type_of_change=='isother_changed':
				isother = request.POST['isother']
				if isother=='true':
					theQ.other = True
				else:
					theQ.other = False
				# print(isother)


			theQ.save()

			# print(qid, " Q changed")
			# print(type_of_change, " type ofchange")
			# print(optid_response)

			response = {"id": int(optid_response)}
			return JsonResponse(response, safe=False)

	return redirect("/")

def modifyconst(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			qid = request.POST['qid']

			isitmyQ = Question.objects.filter(id=int(qid), survey__owner=user)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			theQ = isitmyQ[0]

			constval = request.POST['constdict']
			theQ.constraint = json.loads(constval)
			theQ.save()

			# print(theQ.constraint)

			return HttpResponse("success")

	return redirect("/")


def modifyoneopt(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			optid = request.POST['optid']
			optval = request.POST['optval']

			isitmyOpt = Option.objects.filter(id=int(optid), question__survey__owner=user)
			if isitmyOpt.count()==0:
				return HttpResponse("access denied")

			theopt = isitmyOpt[0]
			theopt.value = optval
			theopt.save()
			return HttpResponse("success")

	return redirect("/")

def delform(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if  sur_id != None:
			Survey.objects.filter(id=int(sur_id), owner=user).delete()
			return redirect("/survey/") 

	return redirect("/")


def preview(request, sur_code=None):
	if not sur_code.isalnum():
		return HttpResponse("<h1>invalid url</h1>")

	elif Survey.objects.filter(access_code=sur_code).exists():

		thesurvey = Survey.objects.filter(access_code=sur_code)[0]
		# print("endate - ", thesurvey.endDate)   # endDate in utc format
		# print("utc time", datetime.now(tz=utc)) # current date time in utc format
		# print("indian time", datetime.now())  # current date time in  India

		if thesurvey.endDate is not None and thesurvey.endDate < datetime.now(tz=utc):
		    # print("form expired.")
		    return HttpResponse("<h2>This survey form is closed<h2>")

		all_itsQ = Question.objects.filter(survey=thesurvey).order_by('order', 'id')

		qdict = {}
		for Q in all_itsQ:
			optlist = Option.objects.filter(question=Q).order_by('id')
			qdict[Q]= optlist

		context = {'survey':thesurvey, 'Qdict':qdict, "qtyparr":qtyparr}
		return render(request, 'survey/preview.html', context) 

	return HttpResponse("This form not exists")


def saveresponse(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif Survey.objects.filter(id=int(sur_id)).exists():
		thesurvey = Survey.objects.get(id=int(sur_id))
		if request.user.is_authenticated:
			user= request.user
		else:
			user=None 

		new_response = Response(user=user, survey=thesurvey)
		new_response.save()

		responseVal = request.POST['responseDict']
		responseDict = json.loads(responseVal)

		for qid, qinfo in responseDict.items():
			isitmyQ = Question.objects.filter(id=int(qid), survey=thesurvey)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			theQ = isitmyQ[0]
			
			if theQ.qtype == 6:
				try:
					textans=datetime.strptime(qinfo['textans'], '%Y-%m-%d').strftime('%d-%b-%Y')
				except:
					textans = qinfo['textans']
			elif theQ.qtype == 7:
				try:
					textans=datetime.strptime(qinfo['textans'], '%H:%M').strftime("%I:%M %p")
				except:
					textans = qinfo['textans']
			else:
				textans= qinfo['textans']

			optdict = {}

			if  len(qinfo['textans'].strip())==0:
				for i, optid in qinfo['optansdict'].items():
					if int(optid) >0:
						isitmyOpt = Option.objects.filter(id=int(optid), question__survey=thesurvey)
						if isitmyOpt.count()==0:
							return HttpResponse("access denied")

						optdict[int(optid)] = isitmyOpt[0].value

			qresponse = PQresponse(response=new_response, question=theQ, 
				textans=textans, options=optdict)
			qresponse.save()

		return HttpResponse("response recorded")

	return HttpResponse("This form not exists")


def response(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user = request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists(): 

			thesurvey = Survey.objects.get(id=int(sur_id), owner=user)
			all_itsQ = Question.objects.filter(survey=thesurvey).order_by("id")  
			all_its_PQres = PQresponse.objects.filter(response__survey=thesurvey)

			numq = all_itsQ.count()

			# data for tabular form 
			# all_itsQ will be used as header of the table
			resdict = {}     # this  dict of object is enough for the table

			all_response = Response.objects.filter(survey=thesurvey)

			for res in all_response:
				oneres = all_its_PQres.filter(response=res).order_by("question__id")
				empty_col = numq - oneres.count()
				resdict[res]=[oneres, range(empty_col)]

			# freqdict={}

			return render(request,'survey/response.html', {"allQ":all_itsQ, "resdict":resdict, "survey":thesurvey})

	return redirect("/")

def graph(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user = request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists(): 

			thesurvey = Survey.objects.get(id=int(sur_id), owner=user)
			choiceQ = Question.objects.filter(survey=thesurvey, qtype__in=[2,3,4]).order_by("id")  
			all_opt_res = PQresponse.objects.filter(response__survey=thesurvey, question__qtype__in=[2,3,4]).order_by("question__id")
			allopt = Option.objects.filter(question__survey=thesurvey)

			# data for graph representation
			freqdict={}   # this  dict of (dict of list) is enough for  graph / frequency table


			for Q in choiceQ:
				if Q.other:
					freqdict[str(Q.id)] = {
						"title": Q.title,
						"type": Q.qtype,
						"other": 0,
						"optfreq":{}
						}
				else:
					freqdict[str(Q.id)] = {
						"title": Q.title,
						"type": Q.qtype,
						"optfreq":{}
						}

			for opt in allopt:
				freqdict[str(opt.question.id)]['optfreq'][str(opt.id)]=[0,opt.value]

			other_res =all_opt_res.exclude(textans='')
			opt_res =all_opt_res.exclude(options={})

			for x in other_res:
				try:
					freqdict[str(x.question.id)]['other'] += 1
				except:
					freqdict[str(x.question.id)]['other'] = 1

			for x in opt_res: 
				for optid, optval in x.options.items():
					try:
						freqdict[str(x.question.id)]['optfreq'][str(optid)][0] += 1
					except:
						# this is rare case, let's say
						# when qtype in [2,3](MCQ) , some responses filled.
						# then qtype change to [0,1] and some responses filled. 
						# then again qtype changed to [2,3], now there r
						# new options , so responses with old options should
						# now be counted in other.
						#  break bcoz {option1,ooptn2,optn3} should be count as one
						try:
							freqdict[str(x.question.id)]['other'] += 1
							break
						except:
							freqdict[str(x.question.id)]['other'] = 1
							break

			if bool(freqdict):
				msz= ""
			else:
				msz="""only checkbox, dropdown & multiple choice type question produces graph. 
				    this form doesn't have any such type of question!"""

			
			# print the frequency table for each Q
			# for qid,qinfo in freqdict.items():
			# 	print("-"*30)
			# 	print("Q-", qid, qinfo['title'])
			# 	print("other", qinfo.get('other'))    # None if other not present

			# 	for n,m in qinfo['optfreq'].items():
			# 		print(n,m)
			# print("graph data sent")

			response = {"status":"valid", "freqdict":freqdict, 'msz':msz}
			return JsonResponse(response, safe=False)

	return redirect("/")


def deloneresponse(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user = request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			resid= request.POST['resid']

			isitmine = Response.objects.filter(id=int(resid), survey__owner=user)
			if isitmine.count()==0:
				return HttpResponse("access denied")

			isitmine.delete()

			return HttpResponse("Response deleted! ")

	return redirect("/")


def tocsv(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user = request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():

			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="response.csv"'

			writer = csv.writer(response)

			thesurvey = Survey.objects.get(id=int(sur_id), owner=user)
			all_itsQ = Question.objects.filter(survey=thesurvey).values_list('title', flat=True) .order_by("id")  
			# print(list(all_itsQ))

			writer.writerow(['response timestamp', 'User'] + list(all_itsQ))

			all_its_PQres = PQresponse.objects.filter(response__survey=thesurvey)

			all_response = Response.objects.filter(survey=thesurvey)

			for res in all_response:
				# print("-"*30)
				thisrow=[res.response_time.strftime('%d-%b-%Y %I:%M %p'), res.user.first_name]
				oneres = all_its_PQres.filter(response=res).order_by("question__id")
				for x in oneres:
					if x.textans != "":
						thisrow.append(x.textans)
					else:
						thisrow.append( ", ".join(list(x.options.values())) )
				# print(thisrow)
				writer.writerow(thisrow)

			return response

	return redirect("/")


def saveorder(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			thesurvey = Survey.objects.get(id=int(sur_id), owner=user)

			qorderval = request.POST['qorderdict']
			qorderdict = json.loads(qorderval)
			for order, idd in qorderdict.items():
				isitmyQ = Question.objects.filter(id=int(idd), survey__owner=user)
				if isitmyQ.count()==0:
					return HttpResponse("access denied")

				theQ = isitmyQ[0]
				theQ.order = int(order) + 1
				theQ.save()
				# print(int(order) + 1, idd)

			return HttpResponse("success")

	return redirect("/")

def savestyle(request, sur_id=None):
	if not sur_id.isnumeric():
		return HttpResponse("<h1>invalid url</h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Survey.objects.filter(id=int(sur_id), owner=user).exists():
			thesurvey = Survey.objects.get(id=int(sur_id), owner=user)

			bgcolor = request.POST['bgcolor']
			theme = request.POST['theme']
			headcolor = request.POST['headcolor']

			styleDict = {'theme':theme, 
						'bgcolor':bgcolor, 'head':headcolor}

			thesurvey.style = styleDict
			thesurvey.save()

			return HttpResponse("success")

	return redirect("/")






# this function saves all the data of editor page  at a time
# this a best and works when user click save button
# but incomplete
# def saveform(request, sur_id=None):
	# if not sur_id.isnumeric():
	# 	return HttpResponse("<h1>invalid url</h1>")

# 	elif request.user.is_authenticated: 
# 			user= request.user
# 			if Survey.objects.filter(id=int(sur_id), owner=user).exists():
# 				thesurvey = Survey.objects.get(id=int(sur_id), owner=user)

# 				form_title = request.POST['form_title']
# 				form_desc = request.POST['form_desc']
# 				form_exdate = request.POST['form_exdate']
# 				form_loginreq = request.POST['form_loginreq']
# 				jsonlist = request.POST['jsonlist']

# 				#  update the survey part like title,date
# 				thesurvey.title = form_title
# 				thesurvey.desc = form_desc
# 				if form_exdate != "":
# 					thesurvey.endDate = datetime.strptime(form_exdate, "%Y-%m-%dT%H:%M")
# 				else:
# 					thesurvey.endDate= None
				
# 				if  form_loginreq == "true":
# 					thesurvey.anonymous = True
# 				else:
# 					thesurvey.anonymous = False

# 				thesurvey.save()

# 				# update all question , all options
				
# 				# print(jsonlist)
# 				unsavedQ = json.loads(jsonlist)

# 				# print("-"*25)
# 				# print(unsavedQ)
# 				# print("-"*25)

# 				for Qorder,Qinfo in unsavedQ.items():
# 					if not bool(Qinfo['constraint']):    # check empty dict
# 						constraint=None
# 					else:
# 						constraint = json.dumps(Qinfo['constraint'])

# 					if Qinfo['qid']=='-1': #new Q
# 						theQ = Question(survey=thesurvey,title=Qinfo['title'],
# 								qtype=Qinfo['type'], order=Qorder,required=Qinfo['isreq'],
# 								other=Qinfo['isother'],constraint=constraint)
# 						theQ.save()
# 						print("question no-",Qorder, " new saved")

# 					else:  # already exists
# 						theQ = Question.objects.get(id=Qinfo['qid'])

# 						theQ.title=Qinfo['title']
# 						theQ.qtype=Qinfo['type'] 
# 						theQ.order=Qorder
# 						theQ.required=Qinfo['isreq']
# 						theQ.other=Qinfo['isother']
# 						theQ.constraint=constraint
# 						theQ.save()
# 						print("question no-",Qorder, " old, updated")


# 					for optnum,optinfo in Qinfo['optdic'].items():
# 						if optinfo['optid']=='-1': #new option
# 							newOpt = Option(question=theQ,value=optinfo['optvalue'])
# 							newOpt.save()
# 							print("    optnum no-",optnum, " new saved")
# 						else:  # already exists
# 							theopt = Option.objects.get(id=optinfo['optid'])
# 							theopt.question = theQ
# 							theopt.value = optinfo['optvalue']
# 							theopt.save()
# 							print("    optnum no-",optnum, " old, updated")


# 				print("survey saved successfully")
# 				return HttpResponse("success")

# 	return redirect("/")



# experiment with data-time
# print(timezone.now())

# naive_datetime = datetime.now()
# print(naive_datetime.tzinfo) # None

# print(settings.TIME_ZONE)  # 'UTC'
# aware_datetime = make_aware(naive_datetime)
# print(aware_datetime.tzinfo)  # <UTC>
# print(naive_datetime)
# print(aware_datetime)