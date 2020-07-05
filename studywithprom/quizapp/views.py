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

qtyparr =["Short ans", "Numeric ans", "MCQ single ans", "MCQ multiple ans"]


def hash_int(n):
    mapping = list(range(48,48+10)) + list(range(97,97+26))
    h = str(hash(str(n)))[1:]  # values range from 0 to 9
    random.seed(n)
    str_h = "".join([ chr(mapping[int(x)+random.randint(0,26)]) for x in h ])
    random.seed()
    return str_h


def dashboard(request):
	if request.user.is_authenticated: 
		user = request.user
		allquiz = Quiz.objects.filter(owner=user).order_by("-id").values("id","title","createDate", "access_code")
		return render(request, 'quiz/qdashboard.html', {"allquiz":allquiz}) 

	return redirect("/")


def gotoquiz(request, quiz_id=None):
	# return response(request,quiz_id)
	return redirect("/quiz/response/" + str(quiz_id))


def newquiz(request) :
	if request.user.is_authenticated: 
		user = request.user
		numsrv = Quiz.objects.filter(owner=user).count()
		title = "New Quiz - " + str(numsrv+1)
		new_quiz = Quiz(owner=user, title=title,endDate=None )
		new_quiz.save()
		new_quiz.access_code = hash_int(new_quiz.id)
		new_quiz.save()

		qtitle = "write your question here"
		newQ = QuestionQ(quiz=new_quiz, title=qtitle, qtype=0,
			order=99)
		newQ.save()

		return redirect("/quiz/editor/" + str(new_quiz.id)) 

	return redirect("/")

def editor(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			thequiz = Quiz.objects.get(id=int(quiz_id), owner=user)
			all_itsQ = QuestionQ.objects.filter(quiz=thequiz).order_by('order','id')

			qdict = {}
			for Q in all_itsQ:
				optlist = OptionQ.objects.filter(question=Q).order_by('id')
				qdict[Q]= optlist

			sharinglink = 'https://studywithprom.pythonanywhere.com/quiz/viewform/' + str(thequiz.access_code)

			context={'quiz':thequiz, 'Qdict':qdict,
					  'qtyparr':qtyparr, 'sharinglink':sharinglink}
			return render(request, 'quiz/qeditor.html', context) 

	return redirect("/")

def orderq(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			thequiz = Quiz.objects.get(id=int(quiz_id), owner=user)
			all_itsQ = QuestionQ.objects.filter(quiz=thequiz).order_by('order', 'id')
			context = {'thequiz':thequiz, 'all_itsQ':all_itsQ}

			return render(request, 'quiz/qorderq.html', context) 

	return redirect("/")


def modifyquiz(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")
	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			form_title = request.POST['form_title']
			form_desc = request.POST['form_desc']
			form_exdate = request.POST['form_exdate']

			# print(form_exdate)

			thequiz = Quiz.objects.get(id=int(quiz_id), owner=user)

			#  update the quiz part like title,date
			thequiz.title = form_title
			thequiz.desc = form_desc
			try:
				thequiz.endDate = datetime.strptime(form_exdate, "%Y-%m-%dT%H:%M")
			except:
				thequiz.endDate = None
				# print(e, "some problem in savning date")

			thequiz.save()

			return HttpResponse("success")


	return redirect("/")

def addoneq(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			thequiz = Quiz.objects.get(id=int(quiz_id), owner=user)
			qtitle = "write your question here"
			newQ = QuestionQ(quiz=thequiz, title=qtitle, qtype=0,
				order=99)
			newQ.save()
			# print(newQ.id , " new q created")

			response = {"id": int(newQ.id)}
			return JsonResponse(response, safe=False)

	return redirect("/")

def copyoneq(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			oldqid=request.POST['oldqid']

			isitmyQ = QuestionQ.objects.filter(id=int(oldqid), quiz__owner=user)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			theoldq_foruse = isitmyQ[0]
			theoldq = QuestionQ.objects.get(id=int(oldqid))
			theoldq.id=None
			theoldq.save()          #now this will work as new Q
			# print(theoldq.id," Q clone succeful with id ")

			optidlist = []
			if theoldq.qtype in [2,3]:
				alloldopt = OptionQ.objects.filter(question=theoldq_foruse).order_by("id")
				for opt in alloldopt:
					# print(opt.id, " old opt id")
					newopt = OptionQ(question=theoldq, value=opt.value, isans=opt.isans)
					newopt.save()
					# print(newopt.id, " new opt id")

					optidlist.append(newopt.id)
			
			# print("optidlist = ",optidlist)


			response = {"id": int(theoldq.id), "optidlist":optidlist}
			return JsonResponse(response, safe=False)

	return redirect("/")

def addoneopt(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			qid = request.POST['qid']
			optval = request.POST['optval']

			isitmyQ = QuestionQ.objects.filter(id=int(qid), quiz__owner=user)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			theQ = isitmyQ[0]
			newOpt = OptionQ(question=theQ,value=optval)
			newOpt.save()

			response = {"id": int(newOpt.id)}
			# print(newOpt.id, " new opt added")
			# print(newOpt.value, " new opt added")
			return JsonResponse(response, safe=False)

	return redirect("/")

def removeoneq(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			qid = request.POST['qid']

			isitmyQ = QuestionQ.objects.filter(id=int(qid), quiz__owner=user)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			isitmyQ.delete()
			# print(qid, " Q removed")
			return HttpResponse("success")

	return redirect("/")

def removeoneopt(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			optid = request.POST['optid']

			isitmyOpt = OptionQ.objects.filter(id=int(optid), question__quiz__owner=user)
			if isitmyOpt.count()==0:
				return HttpResponse("access denied")

			isitmyOpt.delete()
			# print(optid, " option removed")
			return HttpResponse("success")

	return redirect("/")


def modifyoneq(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			type_of_change = request.POST['type']
			qid = request.POST['qid']

			isitmyQ = QuestionQ.objects.filter(id=int(qid), quiz__owner=user)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			theQ = isitmyQ[0]

			optid_response = -1

			if type_of_change=='qtitle_changed':
				qtitle = request.POST['qtitle']
				theQ.title = qtitle
				# print(qtitle)

			elif type_of_change=='marks_changed':
				marks = request.POST['marks']
				theQ.pmarks = marks
				
			elif type_of_change=='text_sol_changed':
				text_sol = request.POST['text_sol']
				theQ.answer = text_sol

			elif type_of_change=='optans_changed':
				optid = request.POST['optid']

				isitmyOpt = OptionQ.objects.filter(id=int(optid), question__quiz__owner=user)
				if isitmyOpt.count()==0:
					return HttpResponse("access denied")

				isans = request.POST['isans']
				if isans=='true':
					isans=True
				else:
					isans=False
				if theQ.qtype ==2:
					OptionQ.objects.filter(question=theQ).update(isans=False)
				
				theopt = isitmyOpt[0]
				theopt.isans=isans
				theopt.save()

			elif type_of_change=='qtype_changed':
				newqtype = int(request.POST['qtype'])
				theQ.answer=""
				OptionQ.objects.filter(question=theQ).update(isans=False)


				oldqtype = theQ.qtype
				# print(oldqtype, "oldqtype")
				theQ.qtype = newqtype
				if (oldqtype in [2,3]) and (newqtype in [0,1]):
					OptionQ.objects.filter(question=theQ).delete()
					# print("phle option the, ab nhi he, so del all opt")
				
				elif (oldqtype in [0,1]) and (newqtype in [2,3]):
					optval = "option-1"
					newOpt = OptionQ(question=theQ,value=optval)
					newOpt.save()
					optid_response=newOpt.id

					# print("phle option nhi the, ab he, so create only one new opt")

				# print(newqtype)


			theQ.save()

			# print(qid, " Q changed")
			# print(type_of_change, " type ofchange")
			# print(optid_response)

			response = {"id": int(optid_response)}
			return JsonResponse(response, safe=False)

	return redirect("/")

def modifyoneopt(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			optid = request.POST['optid']
			optval = request.POST['optval']

			isitmyOpt = OptionQ.objects.filter(id=int(optid), question__quiz__owner=user)
			if isitmyOpt.count()==0:
				return HttpResponse("access denied")

			theopt = isitmyOpt[0]
			theopt.value = optval
			theopt.save()
			return HttpResponse("success")

	return redirect("/")

def delform(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
			user= request.user
			if  quiz_id != None:
				Quiz.objects.filter(id=int(quiz_id), owner=user).delete()
				return redirect("/quiz/") 

	return redirect("/")


def preview(request, quiz_code=None):
	if not quiz_code.isalnum():
		return HttpResponse("<h1> invalid url </h1>")
	elif Quiz.objects.filter(access_code=quiz_code).exists():
		thequiz = Quiz.objects.filter(access_code=quiz_code)[0]
		# print("endate - ", thequiz.endDate)   # endDate in utc format
		# print("utc time", datetime.now(tz=utc)) # current date time in utc format
		# print("indian time", datetime.now())  # current date time in  India

		if thequiz.endDate is not None and thequiz.endDate < datetime.now(tz=utc):
		    # print("form expired.")
		    return HttpResponse("<h2>This quiz  is closed<h2>")


		all_itsQ = QuestionQ.objects.filter(quiz=thequiz).order_by('order', 'id')

		qdict = {}
		for Q in all_itsQ:
			optlist = OptionQ.objects.filter(question=Q).order_by('id')
			qdict[Q]= optlist

		context = {'quiz':thequiz, 'Qdict':qdict}
		return render(request, 'quiz/qpreview.html', context) 

	return HttpResponse("This quiz not exists")


def saveresponse(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif Quiz.objects.filter(id=int(quiz_id)).exists():
		thequiz = Quiz.objects.get(id=int(quiz_id))
		if request.user.is_authenticated:
			user= request.user
		else:
			user=None
		std_code = request.POST['student_code']

		new_response = ResponseQ(user=user, quiz=thequiz, std_code=std_code)
		new_response.save()
		new_response.access_code = hash_int(new_response.id)
		new_response.save()

		responseVal = request.POST['responseDict']
		responseDict = json.loads(responseVal)

		for qid, qinfo in responseDict.items():

			isitmyQ = QuestionQ.objects.filter(id=int(qid), quiz=thequiz)
			if isitmyQ.count()==0:
				return HttpResponse("access denied")

			theQ = isitmyQ[0]
			
			textans= qinfo['textans']

			optdict = {}

			if  len(qinfo['textans'].strip())==0:
				for i, optid in qinfo['optansdict'].items():
					if int(optid) >0:
						isitmyOpt = OptionQ.objects.filter(id=int(optid), question__quiz=thequiz)
						if isitmyOpt.count()==0:
							return HttpResponse("access denied")

						optdict[int(optid)] = isitmyOpt[0].value

			qresponse = PQresponseQ(response=new_response, question=theQ, 
				textans=textans, options=optdict)
			qresponse.save()

		resultlink = 'http://192.168.43.35:8000/quiz/result/' + new_response.access_code


		response = {'msz':"response recorded", "resultlink":resultlink}
		return JsonResponse(response, safe=False)

	return HttpResponse("This quiz not exists")


def response(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user = request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists(): 

			thequiz = Quiz.objects.get(id=int(quiz_id), owner=user)
			all_itsQ = QuestionQ.objects.filter(quiz=thequiz).order_by("id")  
			all_its_PQres = PQresponseQ.objects.filter(response__quiz=thequiz)

			numq = all_itsQ.count()

			# data for tabular form 
			# all_itsQ will be used as header of the table
			resdict = {}     # this  dict of object is enough for the table

			all_response = ResponseQ.objects.filter(quiz=thequiz)

			for res in all_response:
				oneres = all_its_PQres.filter(response=res).order_by("question__id")
				empty_col = numq - oneres.count()
				resdict[res]=[oneres, range(empty_col)]

			# freqdict={}

			return render(request,'quiz/qresponse.html', {"allQ":all_itsQ, "resdict":resdict, "quiz":thequiz})

	return redirect("/")

def graph(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user = request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists(): 

			thequiz = Quiz.objects.get(id=int(quiz_id), owner=user)
			choiceQ = QuestionQ.objects.filter(quiz=thequiz, qtype__in=[2,3]).order_by("id")  
			all_opt_res = PQresponseQ.objects.filter(response__quiz=thequiz, question__qtype__in=[2,3]).order_by("question__id")
			allopt = OptionQ.objects.filter(question__quiz=thequiz)

			# data for graph representation
			freqdict={}   # this  dict of (dict of list) is enough for  graph / frequency table


			for Q in choiceQ:
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
						# now be counted in other .
						try:
							freqdict[str(x.question.id)]['other'] += 1
							break
						except:
							freqdict[str(x.question.id)]['other'] = 1
							break

			if bool(freqdict):
				msz= ""
			else:
				msz="""only MCQ type question produces graph. 
				    this quiz doesn't have any such type of question!"""

			
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


def deloneresponse(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user = request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			resid= request.POST['resid']

			isitmine = ResponseQ.objects.filter(id=int(resid), quiz__owner=user)
			if isitmine.count()==0:
				return HttpResponse("access denied")


			isitmine.delete()

			return HttpResponse("ResponseQ deleted! ")

	return redirect("/")


def tocsv(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user = request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():

			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="response.csv"'

			writer = csv.writer(response)

			thequiz = Quiz.objects.get(id=int(quiz_id), owner=user)
			all_itsQ = QuestionQ.objects.filter(quiz=thequiz).values_list('title', flat=True) .order_by("id")  
			# print(list(all_itsQ))

			writer.writerow(['id', 'response timestamp', 'User'] + list(all_itsQ))

			all_its_PQres = PQresponseQ.objects.filter(response__quiz=thequiz)

			all_response = ResponseQ.objects.filter(quiz=thequiz)

			for res in all_response:
				# print("-"*30)
				thisrow=[res.id, res.response_time.strftime('%d-%b-%Y %I:%M %p'), res.user.first_name]
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


def saveorder(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			thequiz = Quiz.objects.get(id=int(quiz_id), owner=user)

			qorderval = request.POST['qorderdict']
			qorderdict = json.loads(qorderval)
			for order, idd in qorderdict.items():
				theQ = QuestionQ.objects.get(id=int(idd))
				theQ.order = int(order) + 1
				theQ.save()
				# print(int(order) + 1, idd)

			return HttpResponse("success")

	return redirect("/")

def savestyle(request, quiz_id=None):
	if not quiz_id.isnumeric():
		return HttpResponse("<h1> invalid url </h1>")

	elif request.user.is_authenticated: 
		user= request.user
		if Quiz.objects.filter(id=int(quiz_id), owner=user).exists():
			thequiz = Quiz.objects.get(id=int(quiz_id), owner=user)

			bgcolor = request.POST['bgcolor']
			theme = request.POST['theme']
			headcolor = request.POST['headcolor']

			styleDict = {'theme':theme, 
						'bgcolor':bgcolor, 'head':headcolor}

			thequiz.style = styleDict
			thequiz.save()

			return HttpResponse("success")

	return redirect("/")
	


def result(request, acs_code=None):
	if ResponseQ.objects.filter(access_code=acs_code).exists():
		theres = ResponseQ.objects.filter(access_code=acs_code).order_by('-id')[0]

		thequiz = theres.quiz
		all_itsQ = QuestionQ.objects.filter(quiz=thequiz).order_by('order', 'id')
		myPQans = PQresponseQ.objects.filter(response=theres)

		qdict = {}
		for Q in all_itsQ:
			thisQres = myPQans.filter(question=Q)
			if thisQres.count()==1:
				if Q.qtype in [0,1]:
					if len(Q.answer)==0:
						his_marks=0
						# check student answer only if teacher has fixed answer else marks=0
					elif (Q.answer).lower() == (thisQres[0].textans).lower():
						his_marks=Q.pmarks
					else:
						his_marks=0
					if Q.qtype==1:
						try:
							if float(Q.answer) == float(thisQres[0].textans):
								his_marks=Q.pmarks
						except:
							pass

					qdict[Q]=[True, his_marks, thisQres[0].textans]

				elif Q.qtype in [2,3]:
					optlist = OptionQ.objects.filter(question=Q).order_by('id')
					correct_opt = list(optlist.filter(isans=True).order_by('id').values_list('id', flat=True))
					hisans_opt = sorted(list(map(int, thisQres[0].options.keys())))
					
					if len(correct_opt) ==0:
						his_marks = 0
					elif correct_opt == hisans_opt:
						his_marks = Q.pmarks 
					else:
						his_marks = 0

					optstatus =[]    # list of list [ Option , ishisans?]
					for opt in optlist:
						optstatus.append([opt, opt.id in hisans_opt])

					qdict[Q] = [True, his_marks, optstatus]

					# print(his_marks, hisans_opt, correct_opt,optstatus, sep="\n")

				
			elif thisQres.count()==0:
				qdict[Q]=[False, 0]
			else:
				print("some error")

		total_marks = sum( x[1] for x in qdict.values())
		max_marks = sum(x.pmarks for x in  qdict.keys())

		context = {'quiz':thequiz, 'Qdict':qdict, 'std_code': theres.std_code,
				   'total_marks':total_marks, 'max_marks':max_marks }
		return render(request, 'quiz/qresult.html', context) 
	else:
		return HttpResponse("<h1> invalid url </h1>")
