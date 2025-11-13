"""""
模块作用：实现Double-Bicycle LDPC码构造与若干已知优良参数的便捷生成函数。
"""""
import galois
import numpy as np
from extendedstim.Code.LinearCode.LinearCode import LinearCode
from extendedstim.tools.GaloisTools import shift, solve, distance


class DoubleBicycleCode(LinearCode):
    def __init__(self,n:int,a_occupy:list,b_occupy:list)->None:
        """""
        input.n：循环矩阵的大小
        input.a_occupy：循环矩阵A中1的位置
        input.b_occupy：循环矩阵B中1的位置
        output：无（构造对象）
        """""
        self.a_occupy=a_occupy.copy()
        self.b_occupy=b_occupy.copy()
        self.a_occupy.sort()
        self.b_occupy.sort()
        a_list = [1 if i in self.a_occupy else 0 for i in range(n)]
        b_list = [1 if i in self.b_occupy else 0 for i in range(n)]
        H_up = np.hstack([C(n, a_list), C(n, b_list), C(n, a_list).T, C(n, b_list).T])
        H_down = np.hstack([C(n, b_list).T, C(n, a_list).T, C(n, b_list), C(n, a_list)])
        H = np.vstack([H_up, H_down])
        super().__init__(H)

    #%%  USER：===重载运算符===
    ##  USER：----打印代码----
    def __str__(self):
        n=self.number_bit//4
        S_str_a=''
        for i in self.a_occupy:
            S_str_a+=f"S^{{{i}}}_{{{n}}}"
        S_str_b=''
        for i in self.b_occupy:
            S_str_b+=f"S^{{{i}}}_{{{n}}}"
        return S_str_a+ '\n'+S_str_b

    #%%  USER：===静态方法===
    ##  USER：----生成好的代码----
    @staticmethod
    def good_code(n):
        """""
        input.n：循环尺寸
        output：DoubleBicycleCode 或 None
        """""
        if n==23:  # d=14,k=4
            return DoubleBicycleCode(23,[0,9],[21,22])
        elif n==11:  # d=8,k=4
            return DoubleBicycleCode(11,[5,7],[2,7])
        elif n==17:  # d=10,k=4
            return DoubleBicycleCode(17,[2,4],[9,16])
        elif n==36:  # d=12,k=8
            return DoubleBicycleCode(36,[2,19],[1,12])
        else:
            return None

##  USER：===构造多项式的变量元===
def S(n):
    """""
    input.n：尺寸
    output：GF(2)置换矩阵 S (1步移位)
    """""
    return shift(n,1)


##  USER：===构造cyclic matrix===
def C(n,a_list):
    """""
    input.n：尺寸
    input.a_list：长度为n的01序列，指示多项式系数
    output：GF(2)循环矩阵 C(n,a)
    """""
    assert len(a_list) == n
    return galois.GF2(np.sum([a*(np.linalg.matrix_power(S(n),i)) for i,a in enumerate(a_list)],axis=0))
