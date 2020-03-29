from django.shortcuts import render
from django.template import loader

# Create your views here.


def login(request):
    return render(request, 'stream/login.html', {})


def musicpage(request):
    return render(request, 'stream/musicpage.html', {})


def logout(request):
    return render(request, 'stream/logout.html', {})

def player(request):
    return render(request, 'stream/player.html', {})
