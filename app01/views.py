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
        req_que_list = json.loads(request.body.decode())
        # print(req_que_list)

        db_que_list = models.Question.objects.filter(questionnaire_id=naire_id)
        db_qid_list = [i.id for i in db_que_list]
        post_qid_list = [i['qid'] for i in req_que_list if i['qid']]
        del_qid_set = set(db_qid_list) - set(post_qid_list)  # 待删除的问题id集合

        for qid in del_qid_set:
            # 删除问题
            models.Question.objects.filter(id=qid).delete()

        for que_dict in req_que_list:
            qid = que_dict['qid']
            title = que_dict['title']
            type = que_dict['type']
            if not qid:
                # 新建问题
                with atomic():
                    new_que_obj = models.Question.objects.create(title=title, type=type, questionnaire_id=naire_id)
                    if que_dict['type'] == 2:
                        for opt_dict in que_dict['options']:
                            models.Option.objects.create(content=opt_dict['content'], value=opt_dict['value'],
                                                         question=new_que_obj)
            elif qid in db_qid_list:
                # 更新问题，有可能存在有人在前端手动修改"qid"的情况，所以要做筛选，只更新数据库中已经存在的问题

                update_query_set = models.Question.objects.filter(id=qid)
                former_que_type = update_query_set.first().type
                now_que_type = que_dict['type']
                update_query_set.update(title=title, type=type)

                # 对问题类型可能出现的变化做处理
                if former_que_type == 2:
                    # 对原单选类问题的修改
                    if now_que_type == 2:
                        req_opt_list = que_dict['options']  # 在前端限制不能提交空值，这里一定不为空

                        db_opt_list = models.Option.objects.filter(question_id=qid)
                        db_oid_list = [i.id for i in db_opt_list]
                        post_oid_list = [i['oid'] for i in req_opt_list]
                        del_oid_set = set(db_oid_list) - set(post_oid_list)
                        for oid in del_oid_set:
                            # 删除选项
                            models.Option.objects.filter(id=oid).delete()

                        for opt_dict in req_opt_list:
                            oid = opt_dict['oid']
                            content = opt_dict['content']
                            value = opt_dict['value']
                            if not oid:
                                models.Option.objects.create(content=content, value=value, question_id=qid)
                            elif oid in db_oid_list:
                                models.Option.objects.filter(id=oid).update(content=content, value=value)
                            else:
                                # 前端"oid"被修改，不做任何操作
                                pass
                    else:
                        # 单选-->其他类型，清空选项
                        models.Option.objects.filter(question_id=qid).delete()
                elif now_que_type == 2:
                    # 其他类型-->单选，创建选项
                    for opt_dict in que_dict['options']:
                        models.Option.objects.create(content=opt_dict['content'], value=opt_dict['value'],
                                                     question_id=qid)
            else:
                # 前端"qid"被修改，不做任何操作
                pass
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
