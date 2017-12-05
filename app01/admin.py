from django.contrib import admin
from .models import UserInfo, ClassRoom, Student, Questionnaire, Question, Option, Answer

admin.site.register([UserInfo, ClassRoom, Student, Questionnaire, Question, Option, Answer])
