# coding=utf-8

from celery import signature, chain, chord, group


def group_task(fun, argslist):
    return group(fun.s(i) for i in argslist)().get()

