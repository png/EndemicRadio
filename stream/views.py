from django.shortcuts import render, redirect
from django.template import loader
from .forms import *
from django.http import HttpResponse

# Create your views here.


def login(request):
    return render(request, 'stream/login.html', {})


def musicpage(request):
    if request.method == 'POST':
        form = PictureForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            #return render(request, 'stream/logout.html', {})

    else:
        form = PictureForm()

    return render(request, 'stream/musicpage.html', {'form': form})


def success(request):
    return HttpResponse('successfully uploaded')


def logout(request):
    return render(request, 'stream/logout.html', {})
