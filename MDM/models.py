#coding=utf-8
from django.db import models

# Create your models here.


class member_type(models.Model):
    mtype = models.CharField(max_length=50)

    def __unicode__(self):
        return self.mtype

class member(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    user_type = models.ForeignKey("member_type", on_delete=models.CASCADE)
    def __unicode__(self):
        return self.username

class member_token(models.Model):
    user = models.OneToOneField(to=member, on_delete=models.CASCADE)
    token = models.CharField(max_length=64)
    def __unicode__(self):
        return self.token


class 主数据表(models.Model):
    内码 = models.BigAutoField(primary_key=True, db_index=True)
    对象UUID = models.CharField(max_length=36)
    属性名称 = models.CharField(max_length=256)
    属性值UUID = models.CharField(max_length=36, null=True)
    属性值 = models.CharField(max_length=256, null=True)
    代替内码 = models.BigIntegerField(default=0)
    属性序号 = models.DecimalField(default=1.0, decimal_places=6, max_digits=19)
    更新人 = models.CharField(max_length=256)
    更新时间 = models.DateTimeField(auto_now_add=True)
    # owner = models.ForeignKey('auth.User', related_name='maindata', on_delete=models.CASCADE)

    class Meta:
        ordering = ('更新时间',)


class TaskLog(models.Model):
    task_id = models.CharField(max_length=128, null=True)
    parameter = models.CharField(max_length=500, null=True)
    log_date = models.DateTimeField()

    def __str__(self):
        return {'task_id': self.task_id}


class VisitLog(models.Model):
    computer_name = models.CharField(max_length=256, null=True)
    os = models.CharField(max_length=256, null=True)
    request_method = models.CharField(max_length=128, null=True)
    path_info = models.CharField(max_length=256, null=True)
    remote_add = models.CharField(max_length=256, null=True)
    remote_user = models.CharField(max_length=256, null=True)
    log_date = models.DateTimeField()


