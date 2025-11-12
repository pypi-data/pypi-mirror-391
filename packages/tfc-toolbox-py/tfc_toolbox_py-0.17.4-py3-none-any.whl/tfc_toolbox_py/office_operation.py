import pandas as pd


def get_xlsx_column_data(xlsx_address: str, sheet_name: str, header: int, column: str) -> list:
    """
    获取表格某一列的数据
    输入：
        xlsxAddress：表格文件位置；
        sheetName：工作表名称
        header：表头所在行（从0开始）
        column：数据所在列
    输出：
        包含数据的列表
    """
    # 读取Excel文件
    data = pd.read_excel(xlsx_address, sheet_name=sheet_name, header=0, usecols=column, engine='openpyxl')
    # 获取表头名称
    header_name = list(data)[0]
    # 获取数据列表
    data_list = list(data[header_name])
    return data_list
