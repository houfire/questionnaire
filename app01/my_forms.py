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
            "username": wd.TextInput(attrs={"class": 'form-control', "aria-describedby": 'help-username'}),
            "password": wd.PasswordInput(attrs={"class": 'form-control', "aria-describedby": 'help-password'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = models.UserInfo.objects.filter(username=username).exists()
        if user:
            return username
        else:
            raise ValidationError('用户不存在')


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
