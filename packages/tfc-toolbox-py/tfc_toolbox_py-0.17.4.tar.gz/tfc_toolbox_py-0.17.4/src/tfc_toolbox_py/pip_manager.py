import os


def upgrade_check():
    os.system("pipupgrade --check")


def upgrade_package():
    # 根据requirements.txt安装包
    try:
        # 尝试打开requirements.txt以确定文件是否存在
        with open('requirements.txt', 'r') as f:
            pass
    except FileNotFoundError:
        # requirements.txt文件不存在
        print("未发现requirements.txt文件")
    else:
        # requirements.txt文件存在，进行安装
        os.system("pip install -r requirements.txt")
        print("安装完成")

    # 更新所有包
    print("更新包中……")
    try:
        os.system("pipupgrade --latest")
    except ModuleNotFoundError as e:
        # 安装不存在的模块
        os.system("pip install " + e.name)
        # 再次尝试更新
        os.system("pipupgrade --latest")
    finally:
        print("更新完成")
        print("")

    # 生成requirements.txt
    print("生成新的requirements.txt中……")
    os.system("pipreqs . --encoding=utf-8 --force")
    print("生成requirements.txt完成")
