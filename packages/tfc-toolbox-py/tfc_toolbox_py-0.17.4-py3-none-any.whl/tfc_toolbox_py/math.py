"""
Math

This module is some tools related to the math.
"""

def add(num1, num2):
    """
    Sum of two numbers.
    Input two number and get their summation.
    """
    return num1 + num2

def subtract(num1, num2):
    """
    Find the difference between two numbers.
    Input two number and get their difference.
    """
    return num1 - num2

# 设置计算斐波拉契需要的全局字典
fibonacci_dic = {1: 1, 2: 1}

def get_fibonacci(n: int) -> int:
    """
    获取斐波拉契数
    """
    if fibonacci_dic.get(n):
        return fibonacci_dic.get(n)
    else:
        result = get_fibonacci(n - 1) + get_fibonacci(n-2)
        fibonacci_dic[n] = result  # 更新字典
        return result


def get_fibonacci_sequence(n: int) -> list:
    """
    获取斐波拉契数列
    """
    fibonacci_list = []
    for i in range(1, n+1):
        fibonacci_list.append(get_fibonacci(i))
    return fibonacci_list
