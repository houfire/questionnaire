from django.db import models


class Role(models.Model):
    '''
    角色表
    '''
    name = models.CharField(max_length=16, verbose_name='角色名')

    class Meta:
        verbose_name_plural = '角色表'

    def __str__(self):
        return self.name


class UserInfo(models.Model):
    '''
    用户信息表
    '''
    username = models.CharField(max_length=16, verbose_name='用户名')
    password = models.CharField(max_length=16, verbose_name='密码')
    role = models.ManyToManyField(to='Role', verbose_name='担任的角色')

    class Meta:
        verbose_name_plural = '用户信息表'

    def __str__(self):
        return self.username


class ClassRoom(models.Model):
    '''
    班级表
    '''
    caption = models.CharField(max_length=15, verbose_name='班级名')
    headmaster = models.ForeignKey(to='UserInfo', verbose_name='班主任')

    class Meta:
        verbose_name_plural = '班级表'

    def __str__(self):
        return self.caption


class Student(models.Model):
    '''
    学生表
    '''
    name = models.CharField(max_length=10, verbose_name='姓名')
    classroom = models.ForeignKey(to='ClassRoom', verbose_name='所属班级')
    user = models.OneToOneField(to='UserInfo', verbose_name='关联的用户')

    class Meta:
        verbose_name_plural = '学生表'

    def __str__(self):
        return self.name


class Questionnaire(models.Model):
    '''
    调查问卷表
    '''
    title = models.CharField(max_length=64, verbose_name='问卷标题')
    classroom = models.ForeignKey(to='ClassRoom', verbose_name='发布班级')

    class Meta:
        verbose_name_plural = '问卷表'
        unique_together = ('title', 'classroom')

    def __str__(self):
        return self.title


class Question(models.Model):
    '''
    问题表
    '''
    title = models.CharField(max_length=64, verbose_name='问题标题')
    questionnaire = models.ForeignKey(to='Questionnaire', verbose_name='所属问卷')
    question_types = [
        (1, '打分'),
        (2, '单选'),
        (3, '建议'),
    ]
    type = models.IntegerField(choices=question_types, verbose_name='问题类型')

    class Meta:
        verbose_name_plural = '问题表'

    def __str__(self):
        return self.title


class Option(models.Model):
    '''
    选项—值对应表
    '''
    content = models.CharField(max_length=16, verbose_name='选项名称')
    value = models.CharField(max_length=16, verbose_name='选项值')
    question = models.ForeignKey(to='Question', verbose_name='所属问题')

    class Meta:
        verbose_name_plural = '选项表'

    def __str__(self):
        return self.content


class Answer(models.Model):
    value = models.IntegerField(null=True, blank=True, verbose_name='后台分值')
    option = models.OneToOneField(to='Option', verbose_name='对应选项', null=True)
    content = models.CharField(max_length=64, null=True, blank=True, verbose_name='文本内容')

    question = models.ForeignKey(to='Question', verbose_name='所属问题')
    student = models.ForeignKey(to='Student', verbose_name='对应学生')

    class Meta:
        verbose_name_plural = '问题答案表'

    def __str__(self):
        if self.content:
            return self.content
        else:
            return str(self.value)
