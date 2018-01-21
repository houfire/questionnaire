from django.forms import ModelForm, Form, fields, ValidationError
from django.forms import widgets as wd

from app01 import models


class LoginForm(ModelForm):
    '''登录页面'''

    class Meta:
        model = models.UserInfo
        fields = ['username', 'password']
        error_messages = {
            "username": {'required': '用户名不能为空'},
            "password": {'required': '密码不能为空'},
        }
        widgets = {
            "username": wd.TextInput(attrs={"placeholder": 'Username', "class": 'form-control'}),
            "password": wd.PasswordInput(attrs={"placeholder": 'Password', "class": 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = models.UserInfo.objects.filter(username=username).exists()
        if user:
            return username
        else:
            raise ValidationError('用户不存在')


class QuestionnaireForm(ModelForm):
    '''在模态框里做Form检验'''

    class Meta:
        model = models.Questionnaire
        fields = '__all__'
        error_messages = {
            "title": {"required": '标题不能为空'},
            "classroom": {"required": '调查班级不能为空'},
        }
        widgets = {
            "title": wd.TextInput(attrs={"class": 'form-control', "aria-describedby": 'help-title'}),
            "classroom": wd.Select(attrs={"class": 'form-control', "aria-describedby": 'help-classroom'}),
        }


class QuestionForm(ModelForm):
    '''问题编辑页面展示问题'''

    class Meta:
        model = models.Question
        fields = ['id', 'title', 'type']

        widgets = {
            "title": wd.TextInput(attrs={"class": 'form-control'}),
            "type": wd.Select(attrs={"class": 'form-control'}),
        }


class OptionForm(ModelForm):
    '''问题编辑页面展示选项'''

    class Meta:
        model = models.Option
        fields = ['content', 'value']
        widgets = {
            "content": wd.TextInput(attrs={"class": 'form-control'}),
            "value": wd.TextInput(attrs={"class": 'form-control'}),
        }
