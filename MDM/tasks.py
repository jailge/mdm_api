from celery import shared_task
from celery.utils.log import get_task_logger
from MDM.pymdm import pymdm
from MDM import models
from MDM.tools import ms
import datetime
from celery import signature, chain, chord, group
from django.utils import timezone

logger = get_task_logger(__name__)

@shared_task(bind=True)
def addrecord(self, kwargs):
    print(
        'Executing task id {0.id}, kwargs {0.kwargs!r}, hostname {0.hostname}, delivery_info {0.delivery_info}, called_directly {0.called_directly}, reply_to {0.reply_to}'.format(
            self.request))
    logger.info('Executing task id {0.id}, args:{0.args!r}, kwargs:{0.kwargs!r}'.format(self.request))
    # para = [kwargs[k] for k in kwargs]
    # res = ms.group_task(pymdm.insert_record_2_db, kwargs)
    # res = group(pymdm.insert_record_2_db.s(i) for i in kwargs)
    print(kwargs)
    try:
        res = list(map(pymdm.insert_record_2_db, kwargs))
    except Exception as e:
        raise self.retry(exc=e, countdown=5, max_retries=3)
    # res_l = []
    # print(kwargs)
    # for i in kwargs:
    #     res = pymdm.insert_record_2_db(i)
    #     if res:
    #         res_l.append(res)
    #     else:
    #         return False
    # pymdm.insert_record_2_db(uid=kwargs['uuid'], property_name=kwargs['property_name'],
    #                          property_uuid=kwargs['property_uuid'], property_value=kwargs['property_value'],
    #                          author=kwargs['author'])
    # return res_l
    return res


@shared_task(bind=True)
def log_write(self, *args):
    print(
        'Executing task id {0.id}, kwargs {0.kwargs!r}, hostname {0.hostname}, delivery_info {0.delivery_info}, called_directly {0.called_directly}, reply_to {0.reply_to}'.format(
            self.request))
    logger.info('Executing task id {0.id}, args:{0.args!r}, kwargs:{0.kwargs!r}'.format(self.request))
    res = models.VisitLog.objects.create(
        log_date=timezone.now(), computer_name=args[0],
        os=args[1],
        request_method=args[2],
        path_info=args[3],
        remote_add=args[4],
        remote_user=args[5]
    )
    if res:
        return True
    else:
        return False




