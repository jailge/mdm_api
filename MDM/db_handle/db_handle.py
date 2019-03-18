from django.db import connection, transaction


def custom_exec_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    row = cursor.fetchall()
    return row
