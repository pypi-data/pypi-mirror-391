import locale
import os

def clear_screen():
    """
    Clear screen

    You can use this function to clear console, and it can adapt to different OS.
    """
    if os.name == 'nt': # 如果是Windows
        os.system('cls')
    else: # 如果是Mac或Linux
        os.system('clear')

def menu(menu_list: list, language = None) -> int:
    """
    菜单
    这是一个控制台程序，输入一个菜单列表，就可以显示一个菜单，并返回键盘的输入，
    可以处理一些异常情况，如果存在异常，则继续循环，直到不发生异常并返回输入的数字
    输入：要显示的菜单列表，显示的语言
    输出：菜单
    返回：键盘输入的数字
    """

    # 字符串定义
    quit_string = {"English":"Quit", "Chinese":"退出"}
    please_input_number = {"English":"Please input a number:", "Chinese":"请输入序号："}
    number_out_of_range = {"English":"Number out of range.", "Chinese":"输入超出范围。"}
    program_ended = {"English":"Program ended.", "Chinese":"程序已结束。"}
    number_not_integer = {"English":"The input number is not an integer.", "Chinese":"输入的数字不是整数。"}

    # 归一化输入的语言
    if(language != None):
        if(language == "English" or language == "english" or language == "En" or language == "en"):
            default_language = "English"
        elif(language == "Chinese" or language == "chinese" or language == "Ch" or language == "ch"):
            default_language = "Chinese"
        else:
            # 其他不支持的语言，显示中文
            default_language = "Chinese"
    else:
        # 如果未规定语言，那么使用系统语言
        system_language = locale.getlocale()[0]     # 获取系统语言
        if("English" in system_language):
            default_language = "English"
        elif("Chinese" in system_language):
            default_language = "Chinese"
        else:
            # 其他不支持的语言，显示中文
            default_language = "Chinese"

    choice_num = 0

    while True:
        num = 0
        for item in menu_list:
            num += 1
            print(f"{num}.{item}")
        # 通过default_language键匹配quit_string的值
        print(f"0.{quit_string.get(default_language)}")

        try:
            choice_str = ""

            # 通过default_language键匹配please_input_number的值
            choice_str = input(please_input_number.get(default_language))

            choice_num = int(choice_str)
            if choice_num > len(menu_list):
                # 通过default_language键匹配number_out_of_range的值
                print(number_out_of_range.get(default_language))
                continue
            break
        except KeyboardInterrupt:
            os.system("cls")
            # 通过default_language键匹配program_ended的值
            print(program_ended.get(default_language))
            return 0
        except ValueError:
            # 通过default_language键匹配number_not_integer的值
            print(number_not_integer.get(default_language))

    return choice_num
