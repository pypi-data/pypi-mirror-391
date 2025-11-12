import requests
import sqlite3
import webbrowser
from bs4 import BeautifulSoup
import os
import tfc_toolbox_py as tfc
import configparser

def get_academic_info_list():
    """
    获取重邮学术讲座信息，并转换为列表，列表的每一项是字典类型
    返回：重邮学术讲座列表
    """
    base_url = "https://www.cqupt.edu.cn/"
    # 获取网页数据
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # 获取响应数据
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取学术讲座信息
        info_box_left_ml35_rightbox = soup.find('div', class_='info-box left ml35 rightbox')
        content = info_box_left_ml35_rightbox.find('div', class_='content')
        list_box = content.find("div", class_="list-box")
        a_list = list_box.find_all('a')
        
        # 学术讲座信息添加进列表
        academic_info_list = []
        for a_item in a_list:
            # 提取 <a> 标签的href属性值
            a_href = a_item['href']
            # 提取 <a> 标签的title属性值
            a_title = a_item['title']
            # 提取 <span> 标签的date属性值
            span_date = a_item.find("span", class_="time")
            date = span_date.text
            academic_info_list.append({'title': a_title, 'url': base_url + a_href, "date": date})

        return academic_info_list
        
    except requests.RequestException as e:
        # 发送错误，返回空列表
        print(f"请求错误: {e}")
        return []


def get_academic_data_mysql(config_file):
    """
    爬取重邮学术讲座信息，并存储到MySql数据库，显示MySql数据库的数据
    输入：MySql配置文件地址

    配置文件示例：
    ```ini
    [database]
    host = your_database_host
    user = your_database_user
    password = your_database_password
    database = your_database_name
    ```
    """

    # 读取MySql配置文件
    config = configparser.ConfigParser()
    config.read(config_file) # 确保这个文件在 .gitignore 中

    db_config = {
        'host': config['database']['host'],
        'port': config['database']['port'],
        'user': config['database']['user'],
        'password': config['database']['password'],
        'database': config['database']['database']
    }

    # 创建mysql数据库连接
    mysql_info = (db_config['host'], db_config['port'], db_config['user'], db_config['database'], db_config['password'])
    conn = tfc.mysql_manager.create_mysql_connection(mysql_info)

    #创建重邮学术讲座数据表
    create_table_query = """
    CREATE TABLE IF NOT EXISTS academic_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(20) NOT NULL,
        url VARCHAR(100) UNIQUE NOT NULL,
        date VARCHAR(20) NOT NULL,
        read_flag BOOLEAN
    )
    """
    tfc.mysql_manager.execute_query(conn, create_table_query)

    # 从网页获取重邮学术讲座信息
    academic_info_list = get_academic_info_list()

    # 向数据库插入重邮学术讲座数据
    for academic_info_item in academic_info_list:
        # 先检查是否存在重复
        # 根据url检查重复项，而非title
        result = tfc.mysql_manager.execute_query(conn, 'SELECT COUNT(*) FROM academic_info WHERE url = %s', (academic_info_item["url"],))
 
        if result[0][0] == 0:
            # 数据库不存在相同项，插入新数据
            query = "INSERT INTO academic_info (title, url, date, read_flag) VALUES (%s, %s, %s, %s)"
            params = (academic_info_item["title"], academic_info_item["url"], academic_info_item["date"], 0)
            tfc.mysql_manager.execute_query(conn, query, params) #插入数据，并返回受影响的行数

    # 查询数据库里所有重邮学术讲座信息
    query = "SELECT * FROM academic_info"
    academic_info_results_list = tfc.mysql_manager.execute_query(query)

    # 显示重邮学术讲座信息列表
    if(not len(academic_info_results_list)):
        # 信息列表为空
        print("学术讲座信息为空")
    else:
        #信息列表不为空
        for academic_info_item in academic_info_results_list:
            # 元组转字符串
            academic_info_title = academic_info_item[1]
            academic_info_url = academic_info_item[2]
            academic_info_date = academic_info_item[3]
            academic_info_read_flag = academic_info_item[4]

            print(f"（{"已读" if academic_info_read_flag else "未读"}）{academic_info_title}（{academic_info_date}）")
            print(academic_info_url)

def get_cqupt_new_list():
    """
    通过API获取重邮新闻，并转换为列表，列表的每一项是字典类型
    返回：重邮新闻列表
    """
    # 从网页获取重邮新闻信息
    news_list = []
    response = requests.get('https://news.cqupt.edu.cn/index/cqupt/public/news/top/get')
    for item in reversed(response.json()['data']['list']):
        news_list.append({'date':item['addtime'], "title":item['title'], "url":item['url'], "read_flag":0})
    return news_list
    

def get_cqupt_news_sqlite(sqlite_database_address):
    """
    获取重邮新闻并管理，因为不需要同步内容，所以使用本地的sqlite数据库
    输入：数据库地址
    显示：重邮新闻内容
    返回：无
    """

    # 存储读取到的数据
    with sqlite3.connect(sqlite_database_address) as conn:
        cursor = conn.cursor()

        # 创建表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cqupt_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            addtime TEXT NOT NULL,
            title TEXT UNIQUE NOT NULL,
            url TEXT UNIQUE NOT NULL,
            read_flag INTEGER
        )
        ''')

        # 获取重邮新闻列表
        news_list = get_cqupt_new_list()
        
        # 遍历列表
        for news_item in news_list:
            # 先检查是否存在重复
            cursor.execute('SELECT COUNT(*) FROM cqupt_news WHERE title = ?', (news_item[1],))
            result = cursor.fetchone()
            
            if result[0] == 0:
                # 数据库不存在相同项，插入新数据
                cursor.execute('INSERT INTO cqupt_news (addtime, title, url, read_flag) VALUES (?, ?, ?, ?)', news_item)
                conn.commit()

        while(1):
            cursor.execute("SELECT * FROM cqupt_news")
            results = []
            results = cursor.fetchall()
            # 逆序遍历
            for item in reversed(results):
                # 数据格式说明:列表第0位是id,第1位是日期,第2位是标题,第3位是链接,第4位是读状态标志
                print(f"{item[0]}.({"已读" if item[4] == 1 else "未读"})（{item[1]}）{item[2]}")
                print(f"{item[3]}")
                print("")
        
            news_id = input("请输入要查看的新闻ID(输入0退出,-1标记所有新闻为已读):")
            # 清屏
            tfc.console.clear_screen()
            if(news_id == "-1"):
                # 更新某一列的所有数据为固定值
                cursor.execute("UPDATE cqupt_news SET read_flag = 1")
            elif(news_id == "0"):
                break
            elif(news_id != "0" or news_id != "-1"):
                cursor.execute("SELECT * FROM cqupt_news WHERE id = ?", (news_id,))
                row = cursor.fetchone()
                # 打开链接
                webbrowser.open(row[3])
                # 更新读状态标志
                cursor.execute("UPDATE cqupt_news SET read_flag = ? WHERE id = ?",(1, news_id))
            
def get_cqupt_schedule_text(id_num: str, week_num: int) -> None:
    """
    Input student id and week number, and get schedule text.
    :param id_num: Student ID number.
    :param week_num: Which week of this semester. If it is 0, you can get curriculum of all weeks.
    :return: None
    """

    # 课表查询网站
    base_url = "http://jwzx.cqupt.edu.cn/kebiao/kb_stu.php?xh="

    # 头部信息
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    }

    # 使用requests库发送GET请求
    response = requests.get(base_url + id_num, headers=headers)

    # 检查请求是否成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.content, "html.parser")

        # 查找含有特定class的table标签
        table_tags = soup.find_all('table')
        # 遍历table标签
        for table in table_tags:
            lesson = 0
            # 在table标签里面找tr标签
            tr_tags = table.find_all('tr')
            # 遍历所有找到的tr标签
            for tr in tr_tags:
                day = 0
                lesson += 1
                # 在tr标签中找所有td标签
                td_tags = tr.find_all("td")
                # 遍历所有td标签
                for td in td_tags:
                    day += 1
                    # 在所有td标签中找到所有div标签
                    div_tags = td.find_all("div", class_='kbTd')
                    # 打印所有div标签的内容
                    for div in div_tags:
                        week = 0
                        weekList = []
                        # 获取div标签的zc属性
                        zc_attribute = div.get('zc')
                        # 将zc属性转换为列表，并遍历
                        for item in list(zc_attribute):
                            week += 1
                            # 判断要查询的周数是否为0
                            if week_num != 0:
                                # 如果要查询的周数不为0，则只显示weekNum那一周的课表
                                if item != "0" and week == week_num:
                                    weekList.append(str(week))
                            elif week_num == 0:
                                # 如果要查询的周数为0，则显示所有周的课表
                                if item != "0":
                                    weekList.append(str(week))

                        lesson_name_record_tag = 0  # 课程名称记录标签
                        lesson_name_list = []  # 课程名称的字符串分解为字符后组成的列表
                        # 遍历div标签的文本，strip=True会移除前后的空白字符
                        for unit in div.get_text(strip=True):
                            # 设置标签为不向list添加内容
                            if unit == '地':
                                # 遇到字符“地”时，不向list添加内容
                                lesson_name_record_tag = 0
                            # 在标签为1时，向list添加内容
                            if lesson_name_record_tag == 1:
                                lesson_name_list.append(unit)
                            # 设置标签为向list添加内容
                            if unit == '-':
                                # 遇到字符“-”时，向list添加内容
                                lesson_name_record_tag = 1
                        # 将课程名称的字符串分解为字符后组成的列表转换成字符串
                        lesson_name_str = "".join(lesson_name_list)

                        # 在div标签中找font标签，确定一次课是几节课连上
                        font_tags = div.find_all("font")
                        # 遍历所有font标签，并获取font标签中的文本
                        for font in font_tags:
                            # 如果文本为空，则2节连上，如果文本第一个字符为“4”，则四节连上
                            lessonsNum = font.get_text()

                        # 课程不为空，则输出
                        if len(weekList) != 0:
                            print(f"第{",".join(weekList)}周，周{str(day - 1)}，", end="")
                            try:
                                # font标签中获得的字符串为“4节连上”
                                lessonsNum[0] == "4"
                                print(
                                    f"第{(lesson - 2) * 2 - 1}、{(lesson - 2) * 2}、{(lesson - 2) * 2 + 1}、{(lesson - 2) * 2 + 2}节")
                            except IndexError:
                                # font标签中获得的字符串为空，说明2节连上
                                print(f"第{(lesson - 1) * 2 - 1}、{(lesson - 1) * 2}节")
                            print(f"课程名称：{lesson_name_str}")
    else:
        print('Failed to retrieve the webpage.')
        print(f"StateCode:{response.status_code}")
