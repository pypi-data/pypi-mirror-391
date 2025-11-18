"""""
模块作用：实现Majorana CSS码的距离估计、逻辑算符推导与若干构造器（由线性码/校验矩阵/标准例子）。
"""""
import numpy as np
from extendedstim.Code.LinearCode.LinearCode import LinearCode
from extendedstim.Code.QuantumCode.MajoranaCode import MajoranaCode
from extendedstim.Code.QuantumCode.QuantumCSSCode import QuantumCSSCode
from extendedstim.Physics.MajoranaOperator import MajoranaOperator
from extendedstim.tools.GaloisTools import distance, orthogonalize, occupy


class MajoranaCSSCode(MajoranaCode, QuantumCSSCode):

    # %%  USER：===构造方法===
    def __init__(self, generators_x, generators_z, physical_number):
        """""
        input.generators_x：X类Majorana稳定子
        input.generators_z：Z类Majorana稳定子
        input.physical_number：费米子位数
        """""
        QuantumCSSCode.__init__(self, generators_x, generators_z, physical_number)

    # %%  USER：===属性方法===
    ##  USER：---求码距---
    @property
    def distance(self):
        """""
        output：int，随机估计（或MIP）
        """""
        return distance(self.check_matrix_x,'random')

    ##  USER：---求码距（x方向）---
    @property
    def distance_x(self):
        """""
        output：int，基于MIP的精确/上界估计
        """""
        return distance(self.check_matrix_x,'mip')

    ##  USER：---求码距（z方向）---
    @property
    def distance_z(self):
        """""
        output：int，基于MIP的精确/上界估计
        """""
        return distance(self.check_matrix_z,'mip')

    ##  USER：---求逻辑算符---
    @property
    def logical_operators(self):
        """""
        output：np.array[MajoranaOperator]，X向和Z向配对拼接
        """""
        _=self._logical_operators_x
        return np.append(self._logical_operators_x,self._logical_operators_z)

    ##  USER：---求逻辑算符（x方向）---
    @property
    def logical_operators_x(self):
        """""
        output：np.array[MajoranaOperator]，X向逻辑算符
        """""
        matrix = self.check_matrix_x
        codewords = matrix.null_space()
        independent_null_basis_list = []
        for vec in codewords:
            rank_before = np.linalg.matrix_rank(matrix)
            matrix = np.vstack([matrix, vec])
            if np.linalg.matrix_rank(matrix) == rank_before + 1:
                independent_null_basis_list.append(vec)
        basis_list = orthogonalize(independent_null_basis_list)
        majorana_logical_operators_x = []
        majorana_logical_operators_z = []
        for i in range(len(basis_list)):
            occupy_temp=occupy(basis_list[i])
            temp = MajoranaOperator.HermitianOperatorFromOccupy(occupy_temp,[])
            majorana_logical_operators_x.append(temp)
            temp = MajoranaOperator.HermitianOperatorFromOccupy([],occupy_temp)
            majorana_logical_operators_z.append(temp)
        self._logical_operators_x = np.array(majorana_logical_operators_x, dtype=MajoranaOperator)
        self._logical_operators_z = np.array(majorana_logical_operators_z, dtype=MajoranaOperator)
        return self._logical_operators_x

    ##  USER：---求逻辑算符（z方向）---
    @property
    def logical_operators_z(self):
        """""
        output：np.array[MajoranaOperator]，Z向逻辑算符
        """""
        _=self._logical_operators_x
        return self._logical_operators_z

    #%%  USER：===静态方法===
    ##  USER：从校验矩阵构造Majorana CSS code
    @staticmethod
    def FromCheckMatrix(check_matrix):
        """""
        input.check_matrix：GF(2) (m,2n)
        output：MajoranaCSSCode
        """""
        generators_x = []
        generators_z = []
        for i in range(len(check_matrix)):
            generators_x.append(MajoranaOperator.HermitianOperatorFromVector(check_matrix[i]))
            generators_z.append(MajoranaOperator.HermitianOperatorFromVector(check_matrix[i]))
        physical_number=check_matrix.shape[1]
        return MajoranaCSSCode(generators_x, generators_z, physical_number)

    ##  USER：用一个线性码生成Majorana CSS code
    @staticmethod
    def FromLinearCode(linear_code):
        """""
        input.linear_code：LinearCode
        output：MajoranaCSSCode
        """""
        assert isinstance(linear_code,LinearCode)
        generators_x = []
        generators_z = []
        check_matrix=linear_code.check_matrix
        for i in range(len(check_matrix)):
            occupy_temp=occupy(check_matrix[i])
            generators_x.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy_temp,[]))
            generators_z.append(MajoranaOperator.HermitianOperatorFromOccupy([],occupy_temp))
        physical_number=check_matrix.shape[1]
        return MajoranaCSSCode(generators_x, generators_z, physical_number)

    @staticmethod
    def SteaneCode():
        """""
        output：Majorana版Steane CSS实例
        """""
        generators_x = [MajoranaOperator([3,4,5,6],[],1),MajoranaOperator([1,2,5,6],[],1),MajoranaOperator([0,2,4,6],[],1)]
        generators_z = [MajoranaOperator([],[3,4,5,6],1),MajoranaOperator([],[1,2,5,6],1),MajoranaOperator([],[0,2,4,6],1)]
        physical_number=7
        result= MajoranaCSSCode(generators_x, generators_z, physical_number)
        result._logical_operators_x=[MajoranaOperator([0,1,2],[],1j)]
        result._logical_operators_z=[MajoranaOperator([], [0, 1, 2], 1j)]
        return result

