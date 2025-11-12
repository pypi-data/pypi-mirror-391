import tfc_toolbox_py as tfc
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
# 使用decimal模块进行高精度浮点数运算
from decimal import Decimal

def create_mysql_connection(mysql_info:tuple):
    """
    创建MySql连接
    输入：创建表的语句，MySql数据库相关信息的元组，包含：host、端口、数据库名、用户名、密码
    返回：MySql连接对象
    使用示例：
    ```Python
    create_table_query
    mysql_info = ("host", "3306", "user", "user" ,"password")
    conn = create_mysql_connection(mysql_info)
    ```
    """
    try:
        connection = mysql.connector.connect(
            host= mysql_info[0],
            port= mysql_info[1],
            database= mysql_info[2],
            user= mysql_info[3],
            password= mysql_info[4]
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
            return connection
    except Error as e:
        print(f"连接错误: {e}")
        return None

def execute_query(connection, query, params=None):
    """
    执行MySql查询
    输入：MySql连接对象、查询语句、参数
    返回：受影响的行数
    使用示例：
        1. 创建表（这一步不可省略）
        ```Python
        create_table_query = \"""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        \"""
        execute_query(conn, create_table_query)
        ```

        2.插入数据示例
        ```python
        query = "INSERT INTO user (name, email) VALUES (%s, %s)"
        params = (name, email)
        return execute_query(connection, query, params) #返回受影响的行数
        ```

        3.查询所有数据示例
        ```Python
        query = "SELECT * FROM my_assets"
        results = execute_query(connection, query)
        ```
    """
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # 如果是SELECT查询，获取结果
        if query.strip().lower().startswith('select'):
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            print("查询执行成功")
            return cursor.rowcount  # 返回受影响的行数
    except Error as e:
        print(f"查询执行错误: {e}")
        connection.rollback()
    finally:
        cursor.close()