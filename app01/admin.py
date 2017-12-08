from django.contrib import admin
from .models import UserInfo, ClassRoom, Student, Questionnaire, Question, Option, Answer, Role

admin.site.register([UserInfo, ClassRoom, Student, Questionnaire, Question, Option, Answer, Role])
