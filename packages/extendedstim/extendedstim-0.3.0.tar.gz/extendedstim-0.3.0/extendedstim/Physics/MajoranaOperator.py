"""""
模块作用：实现Majorana算符在占据表示下的代数运算、厄米性与向量化。
"""""
import galois
import numpy as np
from extendedstim.Physics.Operator import Operator
from extendedstim.tools.TypingTools import islist


class MajoranaOperator(Operator):
    __slots__ = ['occupy_x', 'occupy_z', 'coff']

    #%%  USER：===构造方法===
    def __init__(self, occupy_x, occupy_z, coff):
        """""
        input.occupy_x：γ支撑X索引
        input.occupy_z：γ'支撑Z索引
        input.coff：相位系数 (±1, ±i)
        """""
        super().__init__(occupy_x, occupy_z, coff)

    #%%  USER：===重载运算符===
    ##  USER：----矩阵乘法----
    def __matmul__(self, other:'MajoranaOperator')->'MajoranaOperator':

        ##  ----数据预处理----
        assert isinstance(other, MajoranaOperator)

        ##  ----计算新算符----
        ##  计算新的占据
        occupy_x = np.setxor1d(self.occupy_x, other.occupy_x, assume_unique=True)
        occupy_z = np.setxor1d(self.occupy_z, other.occupy_z, assume_unique=True)
        self_occupy = np.append(self.occupy_x * 2, self.occupy_z * 2 + 1)
        other_occupy = np.append(other.occupy_x * 2, other.occupy_z * 2 + 1)
        self_occupy = np.sort(self_occupy)
        other_occupy = np.sort(other_occupy)

        ##  计算新的系数
        exchange_times = np.sum([np.count_nonzero(self_occupy > temp) for temp in other_occupy])
        if exchange_times % 2 == 1:
            factor = -1
        else:
            factor = 1

        ##  ----返回新算符----
        return MajoranaOperator(occupy_x, occupy_z, self.coff * other.coff * factor)

    ##  USER：---右矩阵乘法---
    def __rmatmul__(self, other:'MajoranaOperator')->'MajoranaOperator':
        assert isinstance(other, MajoranaOperator)
        return other.__matmul__(self)

    ##  USER：---标量乘法---
    def __mul__(self, other:complex|float|int)->'MajoranaOperator':
        assert other == 1 or other == -1 or other == 1j or other == -1j
        return MajoranaOperator(self.occupy_x, self.occupy_z, self.coff * other)

    ##  USER：---右标量乘法---
    def __rmul__(self, other:complex|float|int)->'MajoranaOperator':
        return self.__mul__(other)

    ##  USER：---字符串表示---
    def __str__(self):
        return "MajoranaOperator(occupy_x={},occupy_z={},coff={})".format(self.occupy_x, self.occupy_z, self.coff)

    ##  USER：---相等判断---
    def __eq__(self, other:'MajoranaOperator')->bool:
        assert isinstance(other, MajoranaOperator)
        return np.array_equal(self.occupy_x, other.occupy_x) and np.array_equal(self.occupy_z, other.occupy_z) and self.coff == other.coff

    ##  USER：---取负---
    def __neg__(self):
        return MajoranaOperator(self.occupy_x, self.occupy_z, -self.coff)

    # %%  USER：===属性方法===
    ##  USER：---算符是否是厄米算符---
    @property
    def is_hermitian(self)->bool:

        ##  ----计算厄米性质----
        if np.mod(self.weight * (self.weight - 1) // 2,2) == 0:
            if not (self.coff == 1 or self.coff == -1):
                return False
        else:
            if not (self.coff == 1j or self.coff == -1j):
                return False

        ##  ----返回结果----
        return True

    ##  USER：---求算符的对偶算符---
    @property
    def dual(self)->'MajoranaOperator':
        return MajoranaOperator(self.occupy_z, self.occupy_x, self.coff)

    # %%  USER：===对象方法===
    ##  USER：---将算符映射成一个新的算符，修改index---
    def index_map(self, index)->'MajoranaOperator':
        x, z, coff = super().index_map(index)
        return MajoranaOperator(x, z, coff)

    ##  USER：---复制方法---
    def copy(self)->'MajoranaOperator':
        return MajoranaOperator(self.occupy_x.copy(), self.occupy_z.copy(), self.coff)

    # %%  USER：===静态方法===
    ##  USER：---定义一个厄米算符，从占据处表示---
    @staticmethod
    def HermitianOperatorFromOccupy(occupy_x:list[int]|np.ndarray,
                                    occupy_z:list[int]|np.ndarray)->'MajoranaOperator':

        ##  ----数据预处理----
        assert islist(occupy_x)
        assert islist(occupy_z)

        ##  ----计算系数----
        weight = len(occupy_x) + len(occupy_z)
        if (weight * (weight - 1) // 2) % 2 == 0:
            coff = 1
        else:
            coff = 1j

        ##  ----返回结果----
        return MajoranaOperator(occupy_x, occupy_z, coff)

    ##  USER：---定义一个厄米算符，从向量表示---
    @staticmethod
    def HermitianOperatorFromVector(vector:np.ndarray|galois.GF(2))->'MajoranaOperator':
        ##  ----数据预处理----
        assert isinstance(vector, (np.ndarray, galois.GF(2)))

        ##  ----计算占据----
        occupy_x = np.where(vector[0::2] == 1)[0]
        occupy_z = np.where(vector[1::2] == 1)[0]

        ##  ----返回结果----
        return MajoranaOperator.HermitianOperatorFromOccupy(occupy_x, occupy_z)

    ##  USER：---检查两个厄米算符是否对易---
    @staticmethod
    def commute(A, B):
        """""
        input.A：MajoranaOperator
        input.B：MajoranaOperator
        output：bool，对易返回True
        """""
        assert isinstance(A, MajoranaOperator) and isinstance(B, MajoranaOperator)
        overlap_x = len(np.intersect1d(A.occupy_x, B.occupy_x))
        overlap_z = len(np.intersect1d(A.occupy_z, B.occupy_z))
        weight = (len(A.occupy_x) + len(A.occupy_z)) * (len(B.occupy_x) + len(B.occupy_z))
        judge = overlap_x + overlap_z + weight
        return np.mod(judge, 2) == 0
