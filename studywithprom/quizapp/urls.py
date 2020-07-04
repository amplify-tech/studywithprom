from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('newquiz', views.newquiz, name='newquiz'),
    path('editor/<quiz_id>', views.editor, name='editor'),
    path('orderq/<quiz_id>', views.orderq, name='orderq'),
    path('saveorder/<quiz_id>', views.saveorder, name='saveorder'),
    path('savestyle/<quiz_id>', views.savestyle, name='savestyle'),
    path('delform/<quiz_id>', views.delform, name='delform'),
    path('modifyquiz/<quiz_id>', views.modifyquiz, name='modifyquiz'),
    path('addoneq/<quiz_id>', views.addoneq, name='addoneq'),
    path('addoneopt/<quiz_id>', views.addoneopt, name='addoneopt'),
    path('removeoneq/<quiz_id>', views.removeoneq, name='removeoneq'),
    path('removeoneopt/<quiz_id>', views.removeoneopt, name='removeoneopt'),
    path('modifyoneq/<quiz_id>', views.modifyoneq, name='modifyoneq'),
    path('modifyoneopt/<quiz_id>', views.modifyoneopt, name='modifyoneopt'),
    path('copyoneq/<quiz_id>', views.copyoneq, name='copyoneq'),
    path('response/<quiz_id>', views.response, name='response'),
    path('graph/<quiz_id>', views.graph, name='graph'),
    path('deloneresponse/<quiz_id>', views.deloneresponse, name='deloneresponse'),
    path('tocsv/<quiz_id>', views.tocsv, name='tocsv'),
    path('viewform/<quiz_code>', views.preview, name='preview'),
    path('saveresponse/<quiz_id>', views.saveresponse, name='saveresponse'),
    path('result/<acs_code>', views.result, name='result'),
    path('<quiz_id>', views.gotoquiz, name='gotoquiz'),
    # path('saveform/<quiz_id>', views.saveform, name='saveform'),
]