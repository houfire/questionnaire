import json

from django.shortcuts import render, reverse, redirect, HttpResponse
from django.http import JsonResponse
from  app01 import models
from app01.my_forms import QuestionForm, OptionForm, LoginForm


def login(request):
    '''
    登录
    '''
    if request.method == 'GET':
        login_form = LoginForm()
        return render(request, 'login.html', {"login_form": login_form})
    else:
        login_form = LoginForm(request.POST)
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
            '''第一层生成器，返回每一个问题被QuestionForm处理后的对象'''
            question_list = models.Question.objects.filter(questionnaire=naire_id)
            if not question_list:
                # 如果是新添加的问卷
                que_form = QuestionForm()
                yield {'que_form': que_form}
            else:
                for que_obj in question_list:
                    que_form = QuestionForm(instance=que_obj)
                    temp_dict = {"que_form": que_form, "que_obj": que_obj, "class": 'hidden', "options": None}
                    if que_obj.type == 2:
                        temp_dict['class'] = ''

                        def inner():
                            '''第二层生成器，返回单选类问题的每一个选项被OptionForm处理后的对象'''
                            option_list = models.Option.objects.filter(question=que_obj)
                            for opt_obj in option_list:
                                opt_form = OptionForm(instance=opt_obj)
                                yield {"opt_form": opt_form, 'opt_obj': opt_obj}

                        temp_dict['options'] = inner()

                    yield temp_dict

        return render(request, 'edit.html', {"que_form_yield": outer()})

    else:
        former_que_list = []
        request_list = json.loads(request.body.decode())
        # print(request_list)
        # request_list = [{'qid': '3', 'title': '这是一个单选题', 'type': '2',
        #                  'options': [{'oid': '1', 'content': '选项A', 'value': '1'},
        #                              {'oid': '2', 'content': '选项B新', 'value': '200'}]},
        #                 {'qid': '0', 'title': '新建议', 'type': '3', 'options': []},
        #                 {'qid': '0', 'title': '新打分', 'type': '1', 'options': []}]
        for que_dict in request_list:
            print(que_dict)
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
