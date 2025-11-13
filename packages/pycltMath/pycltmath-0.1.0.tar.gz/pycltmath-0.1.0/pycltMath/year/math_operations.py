class LeapYearChecker:
    """
    闰年判断类
    """

    def __init__(self, year):
        """
        初始化年份

        Args:
            year (int): 要判断的年份
        """
        self.year = year

    def is_leap_year(self):
        """
        判断是否为闰年

        Returns:
            bool: 如果是闰年返回True，否则返回False
        """
        # 闰年规则：
        # 1. 能被4整除但不能被100整除，或者
        # 2. 能被400整除
        if (self.year % 4 == 0 and self.year % 100 != 0) or (self.year % 400 == 0):
            return True
        else:
            return False

