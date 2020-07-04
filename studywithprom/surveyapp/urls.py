from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('newsurvey', views.newsurvey, name='newsurvey'),
    path('editor/<sur_id>', views.editor, name='editor'),
    path('orderq/<sur_id>', views.orderq, name='orderq'),
    path('saveorder/<sur_id>', views.saveorder, name='saveorder'),
    path('savestyle/<sur_id>', views.savestyle, name='savestyle'),
    path('delform/<sur_id>', views.delform, name='delform'),
    path('modifysurvey/<sur_id>', views.modifysurvey, name='modifysurvey'),
    path('addoneq/<sur_id>', views.addoneq, name='addoneq'),
    path('addoneopt/<sur_id>', views.addoneopt, name='addoneopt'),
    path('removeoneq/<sur_id>', views.removeoneq, name='removeoneq'),
    path('removeoneopt/<sur_id>', views.removeoneopt, name='removeoneopt'),
    path('modifyoneq/<sur_id>', views.modifyoneq, name='modifyoneq'),
    path('modifyoneopt/<sur_id>', views.modifyoneopt, name='modifyoneopt'),
    path('modifyconst/<sur_id>', views.modifyconst, name='modifyconst'),
    path('copyoneq/<sur_id>', views.copyoneq, name='copyoneq'),
    path('response/<sur_id>', views.response, name='response'),
    path('graph/<sur_id>', views.graph, name='graph'),
    path('deloneresponse/<sur_id>', views.deloneresponse, name='deloneresponse'),
    path('tocsv/<sur_id>', views.tocsv, name='tocsv'),
    path('viewform/<sur_code>', views.preview, name='preview'),
    path('saveresponse/<sur_id>', views.saveresponse, name='saveresponse'),
    path('<sur_id>', views.gotosrv, name='gotosrv'),
    # path('saveform/<sur_id>', views.saveform, name='saveform'),
] 