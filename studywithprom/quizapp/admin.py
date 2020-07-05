from django.contrib import admin
from .models import *

admin.site.register(Quiz)
admin.site.register(QuestionQ)
admin.site.register(OptionQ)
admin.site.register(ResponseQ)
admin.site.register(PQresponseQ)