from django.urls import path, include
from . import views
from .views import *

app_name = 'stream'
urlpatterns = [
    path('', views.login, name='login'),
    path('musicpage/', views.musicpage, name='musicpage'),
    path('player/<slug:location>', views.player, name='player'),
    path('select/', views.locationSelect, name='selectLocation'),
    path('logout/', views.logout, name='logout'),
    path('about/', views.about, name='about'),
    path('wikipediaUpdate/', views.wikipediaUpdate),
    path('playlist/<slug:regionName>', views.getPlaylistByRegion)
]
