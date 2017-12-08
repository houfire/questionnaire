import json

from django.shortcuts import render, reverse, redirect, HttpResponse
from django.http import JsonResponse
from django.db.transaction import atomic

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

                        def inner(question_obj):
                            '''第二层生成器，返回单选类问题的每一个选项被OptionForm处理后的对象'''
                            option_list = models.Option.objects.filter(question=question_obj)
                            for opt_obj in option_list:
                                opt_form = OptionForm(instance=opt_obj)
                                yield {"opt_form": opt_form, 'opt_obj': opt_obj}

                        temp_dict['options'] = inner(que_obj)  # 这里必须传参，确保生成器内的question_obj一定是本次循环的que_obj

                    yield temp_dict

        return render(request, 'edit.html', {"que_form_yield": outer()})

    else:
        db_que_list = models.Question.objects.filter(questionnaire_id=naire_id)
        request_list = json.loads(request.body.decode())
        # print(request_list)

        request_list0 = [{'qid': 8, 'title': '修改的建议', 'type': 3, 'options': []},
                         {'qid': 23, 'title': 'bb', 'type': 2, 'options': [{'oid': 15, 'content': 'a', 'value': 'b'},
                                                                           {'oid': None, 'content': '新增的选项',
                                                                            'value': '新增的分值'}]},
                         {'qid': None, 'title': '新增的打分', 'type': 1, 'options': []}]

        db_que_id_list = [i.id for i in db_que_list]
        post_que_id_list = [i['qid'] for i in request_list if i['qid']]
        print(db_que_id_list, post_que_id_list)
        del_id_list = set(db_que_id_list) - set(post_que_id_list)  # 待删除的问题id
        print(del_id_list)

        for que_dict in request_list:
            if not que_dict['qid']:
                with atomic():
                    new_que_obj = models.Question.objects.create(title=que_dict['title'], type=que_dict['type'],
                                                                 questionnaire_id=naire_id)
                    if que_dict['type'] == 2:
                        for opt_dict in que_dict['options']:
                            new_opt_obj = models.Option.objects.create(content=opt_dict['content'],
                                                                       value=opt_dict['value'],
                                                                       question=new_que_obj)
            else:
                print('删除或者更新')
        return HttpResponse('post提交')


def del_question(request, qid):
    '''
    删除问卷中的问题
    '''
    res_dict = {'status': None, 'error_msg': None}
    try:
        models.Question.objects.filter(id=qid).delete()
        res_dict['status'] = True
    except Exception as e:
        res_dict['error_msg'] = e
    return JsonResponse(res_dict)


def delete(request):
    '''
    删除问卷
    '''
    res_dict = {'status': None, 'error_msg': None}
    return JsonResponse(res_dict)


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
