from django.urls import path, include
from . import views

app_name = 'stream'
urlpatterns = [
    path('', views.login, name='login'),
    path('musicpage/', views.musicpage, name='musicpage'),
    path('player/', views.player, name='player'),
    path('logout/', views.logout, name='logout')
]
