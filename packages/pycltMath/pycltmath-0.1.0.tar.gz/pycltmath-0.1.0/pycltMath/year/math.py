def back(self):
    temp_equ = self.equation.get()
    self.equation.set(temp_equ[:-1])  # 一个一个删


def getNum(self, arg):
    temp_equ = self.equation.get()  # 输入算式
    temp_result = self.result.get()

    # 判断基本语法错误
    if temp_result != ' ':  # 计算器输入前还没有结果，那么结果区域应该设置为空。
        self.result.set(' ')
    if temp_equ == '0' and (arg not in ['.', '+', '-', '*', '÷']):  # 如果首次输入为0，则紧跟则不能是数字，只是小数点或运算符
        temp_equ = ''
    if len(temp_equ) > 2 and temp_equ[-1] == '0':  # 运算符后面也不能出现0+数字的情形03，09，x
        if (temp_equ[-2] in ['+', '-', '*', '÷']) and (
                arg in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '(']):
            temp_equ = temp_equ[:-1]
    temp_equ = temp_equ + arg
    self.equation.set(temp_equ)


def clear(self):
    self.equation.set('0')
    self.result.set(' ')


def run(self):
    temp_equ = self.equation.get()
    temp_equ = temp_equ.replace('÷', '/')
    if temp_equ[0] in ['+', '-', '*', '÷']:
        temp_equ = '0' + temp_equ
        print(temp_equ)
    try:
        answer = '%.4f' % eval(temp_equ)  # 保留两位小数
        self.result.set(str(answer))
    except (ZeroDivisionError, SyntaxError):  # 其他除0错误，或语法错误返回Error
        self.result.set(str('Error'))

