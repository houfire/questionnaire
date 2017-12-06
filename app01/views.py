from django.shortcuts import render, reverse, redirect, HttpResponse
from django.http import JsonResponse
from  app01 import models, my_forms


def login(request):
    if request.method == 'GET':
        login_form = my_forms.LoginForm()
        return render(request, 'login.html', {"login_form": login_form})
    else:
        login_form = my_forms.LoginForm(request.POST)
        if not login_form.is_valid():
            return render(request, 'login.html', {"login_form": login_form})
        else:
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = models.UserInfo.objects.filter(username=username, password=password).first()
            if not user:
                return redirect(reverse('login'))
            else:
                request.session['username'] = username
                return redirect(reverse('check'))


def index(request):
    return render(request, 'index.html')


def show(request, naire_id):
    questionnaire_obj = models.Questionnaire.objects.filter(id=naire_id).first()
    if not questionnaire_obj:
        return render(request, 'not found.html')
    else:
        question_list = questionnaire_obj.question_set.all()

    return render(request, 'show.html', {"questionnaire_obj": questionnaire_obj, "question_list": question_list})


def edit(request, **kwargs):
    if not kwargs:
        # 如果是添加问卷
        return render(request, 'edit.html')
    else:
        naire_id = kwargs.get('naire_id')
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
    username = request.session.get('username')
    if not username:
        return redirect(reverse('login'))
    else:
        return render(request, 'check.html', {"naire_list": naire_list, "username": username})
