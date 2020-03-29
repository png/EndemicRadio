from django.urls import path, include
from . import views

app_name = 'stream'
urlpatterns = [
    path('', views.login, name='login'),
    path('musicpage/', views.musicpage, name='musicpage'),
    path('player/<slug:location>', views.player, name='player'),
    path('logout/', views.logout, name='logout'),
    path('wikipediaUpdate/', views.wikipediaUpdate),
    path('playlist/<slug:regionName>', views.getPlaylistByRegion)
]
