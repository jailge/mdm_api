# coding=utf-8

def display_meta(request):
    computer_name = request.META.get('COMPUTERNAME')
    os = request.META.get('OS')
    request_method = request.META.get('REQUEST_METHOD')
    path_info = request.META.get('PATH_INFO')
    remote_add = request.META.get('REMOTE_ADDR')
    remote_user = request.META.get('REMOTE_USER')
    return (computer_name, os, request_method, path_info, remote_add, remote_user)
