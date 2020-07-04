from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('editprofile', views.editprofile, name='editprofile'),
] 