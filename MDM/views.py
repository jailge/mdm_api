# coding=utf-8

from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.shortcuts import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import BaseThrottle, SimpleRateThrottle   #限制访问频率
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from MDM.models import 主数据表
from MDM import models
from MDM.serializers import MainDataSerializer
import re, time, hashlib
from MDM.utils.permit import MyPermission, AdminPermission
from MDM.utils.auth import Myauthentication
from MDM.utils.throttle import *
from MDM.pymdm import pymdm
from MDM.common import display_meta
from MDM import tasks
import time, json
from djcelery.models import TaskMeta



# Create your views here.



class LimitView(APIView):
    authentication_classes = []  # 不让认证用户
    permission_classes = []  # 不让验证权限
    throttle_classes = [MyThrottle, ]

    def get(self, request):
        # self.dispatch
        return Response('控制访问频率示例')

    def throttled(self, request, wait):
        """可定制方法设置中文错误"""

        # raise exceptions.Throttled(wait)
        class MyThrottle(exceptions.Throttled):
            default_detail = '请求被限制'
            extra_detail_singular = 'Expected available in {wait} second.'
            extra_detail_plural = 'Expected available in {wait} seconds.'
            default_code = '还需要再等{wait}秒'

        raise MyThrottle(wait)





# 生成Token
def make_token(user):
    ctime = str(time.time())
    hash = hashlib.md5(user.encode("utf-8"))
    hash.update(ctime.encode("utf-8"))
    return hash.hexdigest()


class AuthView(APIView):
    """登录认证"""
    authentication_classes = []
    permission_classes = []
    def dispatch(self, request, *args, **kwargs):
        return super(AuthView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.dispatch
        return '认证列表'
        # return HttpResponse('get is ok')

    def post(self, request, *args, **kwargs):
        ret = {'code': 1000, 'msg': "登录成功", 'token': None}
        try:
            user = request._request.POST.get("username")
            pwd = request._request.POST.get("password")
            obj = models.member.objects.filter(username=user, password=pwd).first()
            if not obj:
                ret['code'] = 1001
                ret['msg'] = "用户名或密码错误"
            else:
                token = make_token(user)
                models.member_token.objects.update_or_create(user=obj, defaults={"token": token})
                ret['token'] = token
        except exceptions as e:
            ret['code'] = 1002
            ret['msg'] = "请求异常"

        return JsonResponse(ret)



class MainDataList(APIView):
    """
    列出所有已存在的数据或创建一个新的数据
    """
    # authentication_classes = [Myauthentication]
    authentication_classes = []
    permission_classes = []
    # throttle_classes = [AnonThrottle,]
    throttle_classes = []
    def get(self, request, format=None):
        # 获取request请求信息
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        result = tasks.log_write.apply_async(args=request_log)
        result = tasks.log_write.apply_async(args=request_log)
        print(request.user)
        maindata = 主数据表.objects.all()
        serializer = MainDataSerializer(maindata, many=True)
        return Response(serializer.data)

    # permission_classes = [AdminPermission]
    def post(self, request, format=None):
        start_time = time.time()
        pattern = '^[^_][\u4E00-\u9FA5A-Za-z_]+$'
        # uid = request.data['对象UUID']

        # 属性名称是属性值进行判断
        # if request.data['属性名称'] == '属性分类':
        #
        #     match_res = re.match(pattern, request.data['属性值'])
        #     if match_res:
        #         serializer = MainDataSerializer(data=request.data)
        #         if serializer.is_valid():
        #             serializer.save()
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)
        #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #     else:
        #         return Response({'wrong para': request.data['属性值']}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        serializer = MainDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print(time.time() - start_time)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MainDataDetail(APIView):
    """
    检索查看、更新或者删除一个记录
    """
    authentication_classes = [Myauthentication]
    permission_classes = [MyPermission]
    throttle_classes = []
    def get_object(self, pk):
        try:
            return 主数据表.objects.get(pk=pk)
        except 主数据表.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        maindata = self.get_object(pk)
        serializer = MainDataSerializer(maindata)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        maindata = self.get_object(pk)
        serializer = MainDataSerializer(maindata, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        maindata = self.get_object(pk)
        maindata.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MdmPost(APIView):
    """
    创建一个新的数据
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    def post(self, request, format=None):
        # 获取request请求信息
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        result = tasks.log_write.apply_async(args=request_log)
        result = tasks.log_write.apply_async(args=request_log)
        paras = request.data.get('MDM')
        # print(paras)
        # 校验UUID存在与否
        uid = paras[0]['uuid']
        if pymdm.check_uuid_exists(uid):
            return Response({'msg': 'UUID %s exist' % uid}, status=status.HTTP_400_BAD_REQUEST)
        # print(request.data)
        start_time = time.time()
        # args = request.data
        # d = {
        #     'uid': args['对象UUID'],
        #     'property_name': args['属性名称'],
        #     'property_uuid': args['属性值UUID'],
        #     'property_value': args['属性值'],
        #     'author': args['更新人'],
        # }
        res = pymdm.insert_record_2_db_para(paras[0])
        print(time.time() - start_time)
        if res:
            return Response(paras, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # return Response(status.HTTP_200_OK)


class PropertyCategoryList(APIView):
    """
    属性分类列表
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    def get(self, request, format=None):
        # 获取request请求信息
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        result = tasks.log_write.apply_async(args=request_log)
        result = tasks.log_write.apply_async(args=request_log)
        return Response(pymdm.get_property_category())


class PropertyDetailList(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    def get(self, request, format=None):
        # print(tuid, type(tuid))
        request_log = display_meta.display_meta(request)
        print(display_meta.display_meta(request))
        args = request.data
        print(args)
        # table_uuid = args['table_uuid']
        result = tasks.log_write.apply_async(args=request_log)
        result = tasks.log_write.apply_async(args=request_log)
        try:
            res = pymdm.get_property_detail(args['tuid'])
        except Exception as e:
            raise e
        res_dic = {}
        # for r in res:
        #     # 生成dic {'e80da4f6-3eef-11e9-b21f-309c23e0570b': {'名称': '物料', '属性分类': '数据大类', '标签': '主数据'},...}
        #     if r['对象UUID'] not in res_dic:
        #         sub_dic = {r['属性名称']: r['属性值']}
        #         res_dic[r['对象UUID']] = sub_dic
        #     else:
        #         res_dic[r['对象UUID']][r['属性名称']] = r['属性值']
        # print(res_dic)
        # res_list = [dict(**{'对象UUID': k}, **res_dic[k]) for k in res_dic]
        if 'uuid' in args:
            uid = args['uuid']
            update_property_list = pymdm.get_property_update_with_uuid(uid)
            if update_property_list:
                # 如果有代替记录列表
                for update_property in update_property_list:
                    # 如果代替内码在内码列表中
                    if update_property['代替内码'] in [r['内码'] for r in res]:
                        # 找到被代替值并去除
                        res.remove([r for r in res if r['内码'] == update_property['代替内码']][0])
                        # 将代替值插入结果列表
                        res.append(update_property)
            # 加工结果列表转换为dic
            for r in res:
                # 生成dic {'e80da4f6-3eef-11e9-b21f-309c23e0570b': {'名称': '物料', '属性分类': '数据大类', '标签': '主数据'},...}
                if r['对象UUID'] not in res_dic:
                    sub_dic = {r['属性名称']: r['属性值']}
                    res_dic[r['对象UUID']] = sub_dic
                else:
                    res_dic[r['对象UUID']][r['属性名称']] = r['属性值']
            if uid in res_dic:
                return Response(res_dic[args['uuid']])
        else:
            uuid_list = []
            # UUID列表去重
            for uu in [r['对象UUID'] for r in res]:
                if uu not in uuid_list:
                    uuid_list.append(uu)
            print(uuid_list)
            # 得到更新值列表
            update_property_list = [pymdm.get_property_update_with_uuid(uid)[0] for uid in uuid_list if pymdm.get_property_update_with_uuid(uid)]
            print(update_property_list)
            if len(update_property_list) > 0:
                for update_property_dic in update_property_list:
                    if update_property_dic['代替内码'] in [r['内码'] for r in res]:
                        # 找到被代替值并去除
                        res.remove([r for r in res if r['内码'] == update_property_dic['代替内码']][0])
                        # 将代替值插入结果列表
                        res.append(update_property_dic)
                    else:
                        res.append(update_property_dic)
            # 加工结果列表转换为dic
            for r in res:
                # 生成dic {'e80da4f6-3eef-11e9-b21f-309c23e0570b': {'名称': '物料', '属性分类': '数据大类', '标签': '主数据'},...}
                if r['对象UUID'] not in res_dic:
                    sub_dic = {r['属性名称']: r['属性值']}
                    res_dic[r['对象UUID']] = sub_dic
                else:
                    res_dic[r['对象UUID']][r['属性名称']] = r['属性值']
            print(res_dic)
            res_list = [dict(**{'对象UUID': k}, **res_dic[k]) for k in res_dic]
            if 'cp' in args and 'ps' in args:
                cp = int(args['cp'])
                ps = int(args['ps'])
                print(cp, ps)
                return Response(res_list[ps*(cp-1):ps*cp])
            else:
                return Response(res_list)


# uuid精确查询
class PropertyDetailUid(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    def get(self, request, format=None):
        # 获取request请求信息
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        result = tasks.log_write.apply_async(args=request_log)
        result = tasks.log_write.apply_async(args=request_log)
        # 获取request参数
        args = request.data
        res = pymdm.get_property_detail_with_uuid(args['uid'])
        res_dic = {}
        for r in res:
            if r['对象UUID'] not in res_dic:
                res_dic['对象UUID'] = r['对象UUID']
                res_dic[r['属性名称']] = r['属性值']
            else:
                res_dic[r['属性名称']] = r['属性值']
        return Response(res_dic)


class PropertyNameList(APIView):
    """
    属性名称列表
    """
    permission_classes = []
    throttle_classes = []
    def get(self, request, format=None):
        # 获取request请求信息
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        result = tasks.log_write.apply_async(args=request_log)
        result = tasks.log_write.apply_async(args=request_log)
        return Response(pymdm.get_property_name())


class SearchQualification(APIView):
    """
    条件查询
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    def get(self, request, format=None):
        # 获取request请求信息
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        result = tasks.log_write.apply_async(args=request_log)
        result = tasks.log_write.apply_async(args=request_log)
        args = request.data
        try:
            uuids_res = pymdm.get_uuids_with_provalue_proname_inputvalue(args['pro_value'], args['pro_name'], args['value'])
        except Exception as e:
            raise e
        print(uuids_res)
        # 原始数据列表 [[{},{}..], [{},{}..]]
        raw_data_list = [pymdm.get_property_detail_with_uuid(uid['对象UUID']) for uid in uuids_res]
        # 得到更新值列表
        # update_property_list = [pymdm.get_property_update_with_uuid(uid)[0] for uid in uuids_res if
        #                             pymdm.get_property_update_with_uuid(uid)]
        # print(update_property_list)
        res_list = []
        for raw_data in raw_data_list:
            res_dic = {}
            # 得到更新值记录列表
            update_property_list = pymdm.get_property_update_with_uuid(raw_data[0].get('对象UUID'))
            if update_property_list:
                # 如果有代替记录 循环替换
                for update_property in update_property_list:
                    if update_property['代替内码'] in [r['内码'] for r in raw_data]:
                        # 找到被代替值并去除
                        raw_data.remove([r for r in raw_data if r['内码'] == update_property['代替内码']][0])
                        # 将代替值插入结果列表
                        raw_data.append(update_property)
            for r in raw_data:
                # 生成dic {'对象UUID':'e80da4f6-3eef-11e9-b21f-309c23e0570b','名称': '物料', '属性分类': '数据大类', '标签': '主数据'}
                if '对象UUID' not in res_dic:
                    res_dic['对象UUID'] = r['对象UUID']
                    res_dic[r['属性名称']] = r['属性值']
                else:
                    res_dic[r['属性名称']] = r['属性值']
            res_list.append(res_dic)
        return Response(res_list)





# 获取参数测试
class Test(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, format=None):
        print(request.data)
        # paras = [request.data[r] for r in request.data]
        paras = request.data.get('MDM')
        print(paras)
        return Response(paras)


# celery测试
class PostTest(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, format=None):
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        res = tasks.log_write.apply_async(args=request_log)
        res = tasks.log_write.apply_async(args=request_log)
        print(display_meta.display_meta(request))
        print(request.data)
        paras = [request.data[r] for r in request.data]
        print(paras)
        para_l = []
        # 处理参数输出格式[[,,,,],[,,,,],...]
        for i in paras:
            p = [str(a) for a in i.split(',')]
            for pp in p:
                if pp == '':
                    p[p.index(pp)] = None
            para_l.append(p)
        print(para_l)
        # 立即推送队列
        result = tasks.addrecord.apply_async(args=[para_l])
        result = tasks.addrecord.apply_async(args=[para_l])
        print(result)
        print(result.id)
        try:
            models.TaskLog.objects.create(task_id=result.id, parameter=paras, log_date=timezone.now())
        except Exception as e:
            pass

        # task_s = TaskMeta.objects.filter(task_id=result.id).values('status', 'result')
        # print(task_s)
        # if task_s[0]['status'] == 'SUCCESS' and task_s[0]['result']:
        #     return Response(paras, status=status.HTTP_201_CREATED)
        if result:
            return Response(paras, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# 使用celery队列新增
class MdmDataPost(APIView):
    """
    创建一个新的数据
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    def post(self, request, format=None):
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        res = tasks.log_write.apply_async(args=request_log)
        res = tasks.log_write.apply_async(args=request_log)
        # print(display_meta.display_meta(request))
        # print(request.data)
        paras = request.data.get('MDM')
        # print(paras)
        # 校验UUID存在与否
        uid = paras[0]['uuid']
        if pymdm.check_uuid_exists(uid):
            return Response({'msg': 'UUID %s exist' % uid}, status=status.HTTP_400_BAD_REQUEST)

        # uid = paras['对象UUID']
        # if not pymdm.check_uuid_exists(uid):
        #     return Response({'msg': 'UUID %s exist' % uid}, status=status.HTTP_400_BAD_REQUEST)
        # para_l = []
        # # 处理参数输出格式[[,,,,],[,,,,],...]
        # for i in paras:
        #     p = [str(a) for a in i.split(',')]
        #     for pp in p:
        #         if pp == '':
        #             p[p.index(pp)] = None
        #     para_l.append(p)
        # print(para_l)
        # 立即推送队列

        # 格式化参数
        # para_dic = paras[0]
        # uid = para_dic.pop('对象UUID')
        # [{'uuid': uid, 'property_name': para_dic[k], 'property_uuid': k} for k in para_dic]

        result = tasks.addrecord.apply_async(args=[paras])
        result = tasks.addrecord.apply_async(args=[paras])
        # print(result)
        print(result.id)
        try:
            models.TaskLog.objects.create(task_id=result.id, parameter=paras, log_date=timezone.now())
        except Exception as e:
            pass

        # task_s = TaskMeta.objects.filter(task_id=result.id).values('status', 'result')
        # print(task_s)
        # if task_s[0]['status'] == 'SUCCESS' and task_s[0]['result']:
        #     return Response(paras, status=status.HTTP_201_CREATED)
        if result:
            return Response(paras, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class DataCategoryNamesList(APIView):
    """
        获取数据大类名称列表
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    def get(self, request, format=None):
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        res = tasks.log_write.apply_async(args=request_log)
        res = tasks.log_write.apply_async(args=request_log)

        return Response(pymdm.get_category_names())


class DataSubCategoryNamesList(APIView):
    """
        根据大类uuid获取子数据名称列表
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    def get(self, request, format=None):
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        res = tasks.log_write.apply_async(args=request_log)
        res = tasks.log_write.apply_async(args=request_log)
        paras = request.data.get('uuid')
        return Response(pymdm.get_sub_category_names_with_uuid(paras))


# 更新
class MdmDataUpdate(APIView):
    """
        更新
        [uuid, {}, {}]
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    def post(self, request, format=None):
        request_log = display_meta.display_meta(request)
        # 推入日志队列
        res = tasks.log_write.apply_async(args=request_log)
        res = tasks.log_write.apply_async(args=request_log)
        para = request.data.get('MDM')
        update_para = para[1:]
        up_data = []
        res_list = pymdm.get_property_detail_with_uuid(para[0])
        d = {}

        for r in res_list:
            if r['属性名称'] not in d:
                d[r['属性名称']] = r
            else:
                d[r['属性名称']] = r
        print(d)
        for up_d in update_para:
            # for dd in d:
            if up_d['property_name'] in d:
                if up_d['property_value'] == d[up_d['property_name']]['属性值']:
                    continue
                else:
                    # 有更新
                    up_d['replace_id'] = d[up_d['property_name']]['内码']
                    up_data.append(up_d)
        result = tasks.addrecord.apply_async(args=[up_data])
        result = tasks.addrecord.apply_async(args=[up_data])
        try:
            models.TaskLog.objects.create(task_id=result.id, parameter=paras, log_date=timezone.now())
        except Exception as e:
            pass
        if result:
            return Response(up_data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

