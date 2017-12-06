from django.shortcuts import render, reverse, redirect, HttpResponse
from django.http import JsonResponse
from  app01 import models


def login(request):
    return render(request, 'login.html')


def index(request):
    return render(request, 'index.html')


def show(request, naire_id):
    questionnaire_obj = models.Questionnaire.objects.filter(id=naire_id).first()
    if not questionnaire_obj:
        return render(request, 'not found.html')
    else:
        question_list = questionnaire_obj.question_set.all()

    return render(request, 'show.html', {"questionnaire_obj": questionnaire_obj, "question_list": question_list})


def edit(request, naire_id):
    questionnaire_obj = models.Questionnaire.objects.filter(id=naire_id).first()
    if not questionnaire_obj:
        return render(request, 'not found.html')
    else:
        question_list = questionnaire_obj.question_set.all()
    return render(request, 'edit.html', {"question_list": question_list})


def delete(request):
    res_dict = {'status': None, 'error_msg': None}
    return HttpResponse(JsonResponse(res_dict))


def check(request):
    naire_list = models.Questionnaire.objects.all()
    return render(request, 'check.html', {"naire_list": naire_list})
