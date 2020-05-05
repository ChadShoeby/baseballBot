from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.



def index(request):
    return HttpResponse("Hello, world. You're at the Front Office index.<br>Here we will put code to manage and run your team.")