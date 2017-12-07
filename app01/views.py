5
from django.shortcuts import render, reverse, redirect, HttpResponse
from django.http import JsonResponse
from  app01 import models
from app01.my_forms import QuestionForm, OptionForm


def login(request):
    '''
    登录
    '''
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
    '''
    主页
    '''
    return render(request, 'index.html')


def add(request):
    '''
    添加问卷
    '''
    return HttpResponse('添加问卷')


def edit(request, naire_id):
    '''
    添加、编辑问卷页面
    '''
    if request.method == 'GET':
        def outer():
            question_list = models.Question.objects.filter(questionnaire=naire_id)
            if not question_list:
                # 如果是新添加的问卷
                que_form = QuestionForm()
                yield {'que_form': que_form}
            else:
                for que_obj in question_list:
                    que_form = QuestionForm(instance=que_obj)
                    temp_dict = {"que_form": que_form, "que_obj": que_obj, "options": None}
                    if que_obj.type == 2:
                        def inner():
                            option_list = models.Option.objects.filter(question=que_obj)
                            for opt_obj in option_list:
                                opt_form = OptionForm(instance=opt_obj)
                                yield {"opt_form": opt_form, 'opt_obj': opt_obj}

                        temp_dict['options'] = inner()

                    yield temp_dict

        return render(request, 'edit.html', {"que_form_yield": outer()})

    else:
        return HttpResponse('post提交')


def del_question(request, qid):
    '''
    删除问卷中的问题
    '''
    res_dict = {'status': None, 'error_msg': None}
    try:
        # models.Question.objects.filter(id=qid).delete()
        print('模拟问题删除成功')
        res_dict['status'] = True
    except Exception as e:
        res_dict['error_msg'] = e
    return HttpResponse(JsonResponse(res_dict))


def delete(request):
    '''
    删除问卷
    '''
    res_dict = {'status': None, 'error_msg': None}
    return HttpResponse(JsonResponse(res_dict))


def check(request):
    '''
    问卷列表
    '''
    naire_list = models.Questionnaire.objects.all()
    username = request.session.get('username')
    if not username:
        return redirect(reverse('login'))
    else:
        return render(request, 'check.html', {"naire_list": naire_list, "username": username})


def show(request, naire_id):
    '''
    投放问卷页面
    '''
    questionnaire_obj = models.Questionnaire.objects.filter(id=naire_id).first()
    if not questionnaire_obj:
        return render(request, 'not found.html')
    else:
        question_list = questionnaire_obj.question_set.all()

    return render(request, 'show.html', {"questionnaire_obj": questionnaire_obj, "question_list": question_list})
