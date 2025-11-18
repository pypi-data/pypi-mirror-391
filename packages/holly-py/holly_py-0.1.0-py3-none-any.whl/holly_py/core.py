"""
核心功能模块
"""


def greet(name: str = "World") -> str:
    """
    生成问候语
    
    Args:
        name: 要问候的名字，默认为 "World"
    
    Returns:
        str: 问候语字符串
    
    Examples:
        >>> greet()
        'Hello, World!'
        >>> greet("Python")
        'Hello, Python!'
    """
    return f"Hello, {name}!"


class HelloWorld:
    """HelloWorld 类示例"""
    
    def __init__(self, name: str = "World"):
        """
        初始化 HelloWorld 实例
        
        Args:
            name: 要问候的名字
        """
        self.name = name
    
    def greet(self) -> str:
        """
        返回问候语
        
        Returns:
            str: 问候语字符串
        """
        return greet(self.name)
    
    def greet_multiple(self, times: int = 1) -> str:
        """
        返回多次问候语
        
        Args:
            times: 重复次数
        
        Returns:
            str: 重复的问候语，用换行符分隔
        """
        return "\n".join([self.greet() for _ in range(times)])


if __name__ == "__main__":
    # 测试代码
    print(greet())
    print(greet("Python"))
    
    hw = HelloWorld("开发者")
    print(hw.greet())
    print(hw.greet_multiple(3))

