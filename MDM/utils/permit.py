# coding=utf-8

from rest_framework.permissions import BasePermission
from rest_framework.permissions import AllowAny
from MDM import models
from rest_framework import exceptions

class MyPermission(BasePermission):
    def has_permission(self, request, view):
        """
                判断是否有权限访问当前请求
                Return `True` if permission is granted, `False` otherwise.
                :param request:
                :param view:
                :return: True有权限；False无权限
                """
        token = request._request.GET.get("token")
        member_type = models.member_type.objects.filter(member__member_token__token=token).values()
        if member_type[0]['mtype'] == "普通" or member_type[0]['mtype'] == "管理员":
            return True

    def has_object_permission(self, request, view, obj):
        """
                视图继承GenericAPIView，并在其中使用get_object时获取对象时，触发单独对象权限验证
                Return `True` if permission is granted, `False` otherwise.
                :param request:
                :param view:
                :param obj:
                :return: True有权限；False无权限
                """
        token = request._request.GET.get("token")
        member_type = models.member_type.objects.filter(member__member_token__token=token).values()
        if member_type[0]['mtype'] == "管理员":
            return True


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        token = request._request.GET.get("token")
        member_type = models.member_type.objects.filter(member__member_token__token=token).values()
        if member_type[0]['mtype'] == "管理员":
            return True