"""
限流
"""
import time
from rest_framework.throttling import BaseThrottle, SimpleRateThrottle   #限制访问频率
from MDM import models

RECORD = {}

class MyThrottle(BaseThrottle):
    def allow_request(self, request, view):
        '''对匿名用户进行限制，每个用户一分钟访问10次 '''
        ctime = time.time()
        self.ip = self.get_ident(request)
        # ip = '1.1.1.1'
        if self.ip not in RECORD:
            RECORD[self.ip] = [ctime]
        else:
            # [152042123,15204212,3152042,123152042123]
            time_list = RECORD[self.ip]
            while True:
                val = time_list[-1]
                if (ctime - 60) > val:
                    time_list.pop()
                else:
                    break
            if len(time_list) > 10:
                return False
            time_list.insert(0, ctime)
        return True

    def wait(self):
        ctime = time.time()
        first_in_time = RECORD[self.ip][-1]
        wt = 60 - (ctime - first_in_time)
        return wt

###########用resetframework内部的限制访问频率##############
class MySimpleRateThrottle(SimpleRateThrottle):
    scope = 'frequency'
    def get_cache_key(self, request, view):
        return self.get_ident(request)



############3#####限流##################3##
class AnonThrottle(SimpleRateThrottle):
    scope = 'wdp_anon'  # 相当于设置了最大的访问次数和时间

    def get_cache_key(self, request, view):
        token = request._request.GET.get("token")
        # member_type = models.member_type.objects.filter(member__member_token__token=token).values()
        user_exist = models.member_token.objects.filter(token=token)
        if user_exist:
        # if request.user:
            return None  # 返回None表示我不限制，登录用户我不管
        # 匿名用户
        return self.get_ident(request)  # 返回一个唯一标识IP


class UserThrottle(SimpleRateThrottle):
    scope = 'wdp_user'

    def get_cache_key(self, request, view):
        # 登录用户
        token = request._request.GET.get("token")
        # member_type = models.member_type.objects.filter(member__member_token__token=token).values()
        user_exist = models.member_token.objects.filter(token=token)
        if user_exist:
        # if request.user:
            return request.user
        return None  # 返回NOne表示匿名用户我不管