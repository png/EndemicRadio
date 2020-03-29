from django.urls import path, include
from . import views
from .views import *

app_name = 'stream'
urlpatterns = [
    path('', views.login, name='login'),
    path('musicpage/', views.musicpage, name='musicpage'),
    path('logout/', views.logout, name='logout'),
    path('success', success, name='success')
]