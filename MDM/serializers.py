# coding=utf-8

from rest_framework import serializers
from django.contrib.auth.models import User
from MDM.models import 主数据表


class UserSerializer(serializers.ModelSerializer):
    pass

class MainDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = 主数据表
        fields = ('内码', '对象UUID', '属性名称', '属性值UUID','属性值','代替内码','属性序号','更新人','更新时间' )