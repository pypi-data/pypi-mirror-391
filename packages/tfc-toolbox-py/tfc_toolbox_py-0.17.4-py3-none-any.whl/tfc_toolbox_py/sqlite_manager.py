import sqlite3


def create_table(database_address: str, table_name: str, id_use_auto_increase: bool, data_name: list, data_type: list) -> None:
    """
    创建数据库
    输入：数据库文件地址，表名称，是否使用自增id，数据列名称，数据列数据类型
    输出：无
    """
    # 两个列表合并为一个列表
    data_list = []
    for name, type in zip(data_name, data_type):
        data_list.append(f"{name} {type}")

    # 如果不存在，将自动创建；如果存在，则直接进行连接。
    conn = sqlite3.connect(database_address)
    cursor = conn.cursor()
    if id_use_auto_increase is True:
        cursor.execute(f'''
            create table if not exists {table_name}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {",".join(data_list)}
            )
        ''')
    elif id_use_auto_increase is False:
        cursor.execute(f'''
            create table if not exists {table_name}(
                {",".join(data_list)}
            )
        ''')
    conn.commit()
    cursor.close()
    conn.close()


def add_data(database_address: str, table_name: str, data_name: list, data: list) -> None:
    """
    向数据库添加数据，一次只能添加一组数据
    输入：数据库文件地址，表名称，数据列名称，数据
    输出：无
    """
    # 列表转元组
    data_name = tuple(data_name)
    data = tuple(data)
    # 增加数据
    conn = sqlite3.connect(database_address)
    cursor = conn.cursor()
    sql = f'insert into {table_name} {data_name} values {data}'
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def modify_data(database_address: str, table_name: str, field, data, id_num: int) -> None:
    """
    修改数据库的数据\n
    输入：数据库名称，表名称，要修改的字段，字段修改后的数据，id\n
    输出：无\n
    """
    # 连接到SQLite数据库
    # 如果数据库不存在，会自动创建
    conn = sqlite3.connect(database_address)

    # 创建一个Cursor
    cursor = conn.cursor()

    # 执行UPDATE语句
    cursor.execute(f"UPDATE {table_name} SET {field} = {data} WHERE id = {id_num}")

    # 提交事务
    conn.commit()

    # 关闭Cursor和Connection
    cursor.close()
    conn.close()


def delete_data_by_id(database_address: str, table_name: str, id_num: int) -> None:
    """
    根据id删除数据库中对应的数据
    输入：数据库文件地址，表名称，id值
    输出：无
    """
    conn = sqlite3.connect(database_address)
    cursor = conn.cursor()
    sql = f"delete from {table_name} where id = {str(id_num)}"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def read_data_to_list(database_address: str, table_name: str) -> list:
    """
    读取数据库全部数据，并输出为列表
    输入：数据库地址，表名称
    输出：列表形式的数据库内容
    """
    data_list = []
    # 如果不存在，将自动创建；如果存在，则直接进行连接。
    conn = sqlite3.connect(database_address)
    cursor = conn.cursor()
    cursor.execute(f'select * from {table_name}')
    for item in cursor:
        data_list.append(item)
    conn.commit()
    cursor.close()
    conn.close()

    return data_list


def read_column_data_to_list(database_address: str, table_name: str, field: str) -> list:
    """
    读取数据库全部数据，并输出为列表
    输入：数据库地址，表名称
    输出：列表形式的数据库内容
    """
    column_data_list = []
    # 如果不存在，将自动创建；如果存在，则直接进行连接。
    conn = sqlite3.connect(database_address)
    cursor = conn.cursor()

    # 执行查询语句，假设我们要从users表中读取name列的所有数据
    cursor.execute(f"SELECT {field} FROM {table_name}")

    # 获取查询结果
    column_data = cursor.fetchall()

    for item in column_data:
        # 读取到的列是元组，需要转换成字符串，再append到列表
        column_data_list.append(str(item[0]))
    conn.commit()
    cursor.close()
    conn.close()

    return column_data_list
