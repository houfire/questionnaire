import json

from django.forms import Form, fields, widgets, ValidationError
from django.shortcuts import render, reverse, redirect, HttpResponse
from django.http import JsonResponse
from django.db.transaction import atomic

from  app01 import models
from app01.my_forms import LoginForm, QuestionnaireForm, QuestionForm, OptionForm


def login(request):
    '''
    登录
    '''
    if request.method == 'GET':
        print(request.GET.get('ReturnURL'))
        login_form = LoginForm()
        return render(request, 'login.html', {"login_form": login_form})
    else:
        rtn_url = request.GET.get('ReturnURL')

        login_form = LoginForm(request.POST)
        if not login_form.is_valid():
            return render(request, 'login_xxx.html', {"login_form": login_form})
        else:
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = models.UserInfo.objects.filter(username=username, password=password).first()
            if not user:
                return redirect(reverse('login'))
            else:
                roles = user.role.values_list('name')
                for role_tup in roles:
                    if '班主任' in role_tup:
                        request.session['userinfo'] = {"username": username, "role": '班主任', "class_id": None}
                        return redirect(reverse('index'))
                    else:
                        request.session['userinfo'] = {"username": username, "role": '学生', "stu_id": user.student.id,
                                                       "class_id": user.student.classroom_id}
                        if rtn_url:
                            return redirect(rtn_url)
                        else:
                            return redirect(reverse('home'))


def logout(request):
    '''
    注销
    '''
    rtn_url = request.GET.get('ReturnURL')
    request.session.flush()
    if rtn_url:
        return redirect('/login/?ReturnURL=' + rtn_url)
    else:
        return redirect(reverse('login'))


def index(request):
    '''
    问卷列表
    '''
    session_dict = request.session.get('userinfo')

    if not session_dict:  # 如果没有用户登录，跳转到登录页面
        return redirect(reverse('login'))

    if session_dict.get('role') == '学生':  # 如果登录的用户是“学生”，跳转至'home'页面
        return redirect(reverse('home'))

    # 在页面展示问卷列表
    username = session_dict.get('username')
    naire_list = models.Questionnaire.objects.all()
    questionnaire_form = QuestionnaireForm()

    return render(request, 'index.html',
                  {"naire_list": naire_list, "username": username, "questionnaire_form": questionnaire_form})


def home(request):
    '''
    主页
    '''
    return render(request, 'home.html')


def add(request):
    '''
    添加问卷
    '''
    if request.is_ajax():
        req_dict = json.loads(request.body.decode('utf8'))

        res_dict = {'status': True, 'error_msg': None}

        title = req_dict.get('title')
        classroom_id = req_dict.get('classroom_id')
        try:
            models.Questionnaire.objects.create(title=title, classroom_id=classroom_id)S
        except Exception as e:
            res_dict['status'] = False
            res_dict['error_msg'] = str(e)

    return JsonResponse(res_dict)


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
        res_dict['error_msg'] = str(e)
    return JsonResponse(res_dict)


def delete(request):
    '''
    删除问卷
    '''
    if request.is_ajax():
        naire_id = request.GET.get('naire_id')
        res_dict = {'status': True, 'error_msg': None}
        try:
            # models.Questionnaire.objects.filter(id=naire_id)
            print('模拟删除成功')
        except Exception as e:
            res_dict['status'] = False
            res_dict['error_msg'] = str(e)

        return JsonResponse(res_dict)


def show(request, class_id, naire_id):
    '''
    投放问卷页面
    '''
    if not request.session.get('userinfo').get('role') == '学生':
        return redirect('/logout/?ReturnURL=' + request.path_info)

    # 对当前URL进行校验############################
    if not models.ClassRoom.objects.filter(id=class_id).exists():
        # 如果url中的班级id不存在
        return render(request, 'not found.html')
    elif not models.Questionnaire.objects.filter(id=naire_id).exists():
        # 如果url中的问卷id不存在
        return render(request, 'not found.html')

    # 对当前打开问卷页面的用户进行校验##############
    session_dict = request.session.get('userinfo')
    user_class_id = session_dict.get('class_id')
    if user_class_id != int(class_id):
        return render(request, 'not found.html', {"warning": "不是本班学生不能填写问卷！"})

    stu_id = session_dict.get('stu_id')
    if models.Answer.objects.filter(student_id=stu_id).exists():
        return render(request, 'not found.html', {"warning": '已经填写过此问卷！'})

    # 动态生成Form组件#############################
    def my_valid(text):
        '''自定义验证规则'''
        if len(text) < 15:
            raise ValidationError('内容不能少于十五字')

    question_list = models.Question.objects.filter(questionnaire_id=naire_id)
    form_dict = {}

    for que_obj in question_list:
        if que_obj.type == 1:
            form_dict['value_%s' % que_obj.id] = fields.ChoiceField(
                label=que_obj.title,
                widget=widgets.RadioSelect,
                choices=[(i, i) for i in range(1, 11)],
                error_messages={"required": '不能为空'}, )
        elif que_obj.type == 2:
            form_dict['option_id_%s' % que_obj.id] = fields.ChoiceField(
                label=que_obj.title,
                widget=widgets.RadioSelect,
                choices=models.Option.objects.filter(question=que_obj).values_list('value', 'content'),
                error_messages={"required": '不能为空'}, )
        else:
            form_dict['content_%s' % que_obj.id] = fields.CharField(
                label=que_obj.title,
                widget=widgets.Textarea,
                error_messages={"required": '不能为空'},
                validators=(my_valid,), )

    ShowForm = type("ShowForm", (Form,), form_dict)  # 动态创建一个Form类

    # 处理HTTP请求################################
    if request.method == 'GET':
        show_form = ShowForm()
        return render(request, 'show.html', {"show_form": show_form})
    else:
        show_form = ShowForm(request.POST)
        if not show_form.is_valid():
            return render(request, 'show.html', {"show_form": show_form})
        else:
            # print(show_form.cleaned_data)
            bulk_obj_list = []
            for k, v in show_form.cleaned_data.items():
                col, qid = k.rsplit('_', 1)
                answer_dict = {"question_id": qid, "student_id": stu_id, col: v}
                bulk_obj_list.append(models.Answer(**answer_dict))
            models.Answer.objects.bulk_create(bulk_obj_list)
        return HttpResponse('感谢参与本次问卷调查！')
