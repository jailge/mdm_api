# coding=utf-8

from MDM.common.msodbc import Odbc_Ms
# from django.conf import settings
from mdm_api import settings
from MDM.db_handle import db_handle
import uuid
from celery.task import task

# msodbc = Odbc_Ms('10.10.7.80', 'swtest', 'sa', 'sa123')
msodbc = Odbc_Ms(settings.DATABASES['default']['HOST'],
        settings.DATABASES['default']['NAME'],
        settings.DATABASES['default']['USER'],
        settings.DATABASES['default']['PASSWORD'])

msodbcread = Odbc_Ms(settings.READER['HOST'], settings.READER['NAME'],
                     settings.READER['USER'], settings.READER['PASSWORD'])


@task
def insert_record_2_db_para(d):
    uid = d.get('uuid')
    property_name = d.get('property_name')
    property_uuid = d.get('property_uuid')
    property_value = d.get('property_value')
    author = d.get('author')
    if property_uuid == '':
        property_uuid = None
    sql = '''
    insert into MDM_主数据表([对象UUID]
      ,[属性名称]
      ,[属性值UUID]
      ,[属性值]

      ,[更新人])
      values(?, ?, ?, ?, ?)
    '''
    para = (uid, property_name, property_uuid, property_value, author)
    return msodbc.ExecNoQuery(sql=sql, para=para)

@task
def insert_record_2_db(d):
    uid = d.get('uuid')
    property_name = d.get('property_name')
    property_uuid = d.get('property_uuid')
    property_value = d.get('property_value')
    replace_id = d.get('replace_id')
    property_no = d.get('property_no')
    author = d.get('author')
    if not property_uuid:
        property_uuid = None
    # uid = d[0]
    # property_name = d[1]
    # property_uuid = d[2]
    # property_value = d[3]
    # replace_id = d[4]
    # property_no = d[5]
    # author = d[6]
    sql = '''
    insert into MDM_主数据表([对象UUID]
      ,[属性名称]
      ,[属性值UUID]
      ,[属性值]
      ,[代替内码]
      ,[属性序号]
      ,[更新人])
      values(?, ?, ?, ?, ?, ?, ?)
    '''
    para = (uid, property_name, property_uuid, property_value, replace_id, property_no, author)
    return msodbc.ExecNoQuery(sql=sql, para=para)


def update_record_with_uid(uid, property_name, property_uuid, property_value, replace_num, property_no, author):
    if msodbc.ExecQuery(sql='select 1 from 主数据表 where [对象UUID]=?', para=uid):
        sql = '''
        insert into 主数据表 (
          [对象UUID]
          ,[属性名称]
          ,[属性值UUID]
          ,[属性值]
          ,[代替内码]
          ,[属性序号]
          ,[更新人])
          values(?, ?, ?, ?, ?, ?, ?)
        '''
        para = (uid, property_name, property_uuid, property_value, replace_num, property_no, author)
        return msodbc.ExecNoQuery(sql=sql, para=para)
    else:
        return False


def delete_record_with_uid(uid, property_name, replace_num, property_no, author):
    if msodbc.ExecQuery(sql='select 1 from 主数据表 where [对象UUID]=?', para=uid):
        sql = '''
            insert into 主数据表 (
              [对象UUID]
              ,[属性名称]
              ,[属性值UUID]
              ,[属性值]
              ,[代替内码]
              ,[属性序号]
              ,[更新人])
              values(?, ?, ?, ?, ?, ?, ?)
            '''
        para = (uid, property_name, None, None, replace_num, property_no, author)
        return msodbc.ExecNoQuery(sql=sql, para=para)
    else:
        return False


# 属性分类列表
def get_property_category():
    sql = '''
    SELECT [表UUID]
      ,[属性名称]
      ,[属性值]
    FROM [swtest].[dbo].[MDM_自动表名映射]
    where 属性名称='属性分类'
    '''
    # raw = db_handle.custom_exec_sql(sql)
    # for
    return msodbcread.ExecQuery(sql)


# 根据uidTable查询
def get_property_detail(tableuuid):
    sql = '''
    declare @tablename varchar(200)
    declare @sql nvarchar(2000)
    set @tablename=?
    set @sql=N'select * from MDM_主数据表
    where 对象UUID in
    (
    select 对象UUID from 
    ' +@tablename+ ')'
    exec sp_executesql @sql
    '''
    return msodbcread.ExecQuery(sql=sql, para=tableuuid)

# 根据对象UUID查询主表更新值
def get_property_update_with_uuid(uid):
    sql = '''
    select * from MDM_主数据表
    where 内码 >
    (   
    select 参数值 from MDM_参数表
    where 参数名称 = '主数据内码更新最大值'

    ) and 对象UUID=?
    '''
    return msodbcread.ExecQuery(sql=sql, para=uid)


# 根据UUID获取对应数据
def get_property_detail_with_uuid(uid):
    sql = '''
    SELECT  [内码]
      ,[对象UUID]
      ,[属性名称]
      ,[属性值UUID]
      ,[属性值]
      ,[代替内码]
      ,[属性序号]
      ,[更新人]
      ,[更新时间]
    FROM [swtest].[dbo].[MDM_主数据表]
    where 对象UUID=?
    '''
    return msodbcread.ExecQuery(sql=sql, para=uid)


# 属性名称列表
""" 编码
# 标签
# 描述
# 名称
# 英文缩写
# 属性分类
# 字段类型
"""
def get_property_name():
    sql = '''
    select distinct 属性名称 from MDM_自动表名映射
    '''
    return msodbcread.ExecQuery(sql)


# 根据属性名称获得表UUID及所含属性值

def get_property_value_with_pname(pname):
    sql = '''
      select *
      from MDM_自动表名映射
      where 属性值=?
    '''
    return msodbcread.ExecQuery(sql=sql, para=pname)


# 根据属性值和名称 查找符合条件的记录(对象UUID集)
# 查找客户
def get_uuids_with_provalue_proname_inputvalue(pro_value, pro_name, input_value):
    sql = """
    declare  @tblName varchar(200)
    declare @sql nvarchar(2000)
    declare @pro_value nvarchar(200)
    declare @pro_name nvarchar(200)
    declare @value nvarchar(200)

    set @pro_value = ?
    set @pro_name = ?
    set @value = ?
    set @tblName = (select 表UUID from MDM_自动表名映射 where 属性值=@pro_value and 属性名称=@pro_name)

    set @sql = 'select 对象UUID from '+ @tblName + ' where 属性值 like ''%' + @value + '%'''

    exec sp_executesql @sql
    """
    return msodbcread.ExecQuery(sql=sql, para=(pro_value, pro_name, input_value))


# 获得数据大类名称
def get_category_names():
    sql = '''
    select * from MDM_主数据表
    where 属性名称='名称' and 对象UUID in(
    select 对象UUID
    from MDM_主数据表
    where 属性值='辅助数据')
    '''
    return msodbcread.ExecQuery(sql)

# 根据大类uuid获取子项名称
def get_sub_category_names_with_uuid(uid):
    sql = '''
    select * from MDM_主数据表
    where 属性名称='名称' and 对象UUID in(
    select 对象UUID from MDM_主数据表
    where 属性值UUID=?)
    '''
    return msodbcread.ExecQuery(sql=sql, para=uid)



# 对象UUID校验是否存在
def check_uuid_exists(uid):
    sql='''
    select 内码
    from MDM_主数据表
    where 对象UUID=?
    '''
    return msodbcread.ExecQuery(sql=sql, para=uid)


if __name__ == '__main__':
    print(get_uuids_with_provalue_proname_inputvalue('减速机参数', '编码', 's'))
