"""
公共API接口 - 不编译，提供完整文档
"""

from . import core_logic

def calculate(x, y):
    """
    计算两个数的和
    
    Args:
        x (int | float): 第一个数字
        y (int | float): 第二个数字
        
    Returns:
        int | float: 两数之和
        
    Examples:
        >>> calculate(10, 20)
        30
        >>> calculate(3.5, 2.5)
        6.0
    """
    return core_logic.complex_calculation(x, y)