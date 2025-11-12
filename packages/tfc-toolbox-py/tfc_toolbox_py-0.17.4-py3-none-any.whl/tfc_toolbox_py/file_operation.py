import json
import os


def read_file_to_list(file_address: str) -> list:
    """
    打开文件，并输出文件内容为列表\n
    输入：文件地址
    输出：列表形式的文件内容
    """
    try:
        f = open(file_address, 'r', encoding="utf-8")
        content = f.read()
        # 将读取内容转化为列表
        file_content = json.loads(content)
    except json.decoder.JSONDecodeError:
        file_content = []
    except FileNotFoundError:
        file_content = []
        f = open(file_address, 'w')
        f.close()
    return file_content


def save_list_to_file(list, file_adress) -> None:
    """
    保存列表到文件
    输入：列表，文件地址
    输出：无
    """
    save_json = open(file_adress, 'w', encoding='utf-8')
    # 通过json.dumps()把dict降级为字符串
    save_json.write(json.dumps(list, indent=4, ensure_ascii=False))
    save_json.close()


def get_file_name_from_folder(folder_path: str, file_extension: str) -> list:
    """
    从文件夹中获取所有文件的名称（不含文件拓展名）
    输入：文件夹路径，文件拓展名
    返回：包含文件名的列表
    """
    files_name_list = []

    # 使用os.listdir()函数获取文件夹中的所有文件和子文件夹
    files_and_folders = os.listdir(folder_path)

    # 遍历文件和子文件夹列表
    for item in files_and_folders:
        # 使用os.path.isfile()函数检查当前项是否为文件
        if os.path.isfile(os.path.join(folder_path, item)):
            # 如果是文件，则append到列表中
            files_name_list.append(item.rstrip("." + file_extension))

    return files_name_list


def get_file_full_name_from_folder(folder_path: str) -> list:
    """
    从文件夹中获取所有文件的完整名称
    输入：文件夹路径，文件拓展名
    返回：包含文件名的列表
    """
    files_name_list = []

    # 使用os.listdir()函数获取文件夹中的所有文件和子文件夹
    files_and_folders = os.listdir(folder_path)

    # 遍历文件和子文件夹列表
    for item in files_and_folders:
        # 使用os.path.isfile()函数检查当前项是否为文件
        if os.path.isfile(os.path.join(folder_path, item)):
            # 如果是文件，则append到列表中
            files_name_list.append(item)

    return files_name_list


def get_file_and_folder_full_name_from_folder(folder_path: str) -> list:
    """
    从文件夹中获取所有文件、文件夹的完整名称
    输入：文件夹路径，文件拓展名
    返回：包含文件名、文件夹名的列表
    """

    # 使用os.listdir()函数获取文件夹中的所有文件和子文件夹
    files_and_folders = os.listdir(folder_path)

    return files_and_folders
