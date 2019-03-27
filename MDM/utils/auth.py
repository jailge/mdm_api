# coding=utf-8

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from MDM import models

class Myauthentication(BaseAuthentication):
    """认证类"""
    def authenticate(self, request):
        token = request._request.GET.get("token")
        token_obj = models.member_token.objects.filter(token=token).first()
        if not token_obj:
            return None
            # raise exceptions.AuthenticationFailed('用户认证失败')
        # restframework会将元组赋值给request,以供后面使用
        return (token_obj.user, token_obj)

    def authenticate_header(self, request):
        pass