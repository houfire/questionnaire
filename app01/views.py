from django.shortcuts import render, reverse, redirect, HttpResponse
from  app01 import models


def index(request):
    return render(request, 'index.html')


def show(request):
    naire_list = models.Questionnaire.objects.all()
    person_num = models.Answer.objects.filter().distinct().count()
    return render(request, 'show.html', {"naire_list": naire_list})


def create(request):
    return render(request, 'create.html')


def edit(request):
    return render(request, 'edit.html')
