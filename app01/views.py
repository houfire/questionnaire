from django.shortcuts import render, reverse, redirect, HttpResponse
from django.http import JsonResponse
from  app01 import models


def index(request):
    return render(request, 'index.html')


def show(request):
    naire_list = models.Questionnaire.objects.all()
    return render(request, 'show.html', {"naire_list": naire_list})


def edit(request, naire_id):
    return render(request, 'edit.html')


def delete(request):
    res_dict = {'status': None, 'error_msg': None}
    return HttpResponse(JsonResponse(res_dict))
