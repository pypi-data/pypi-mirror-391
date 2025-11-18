"""""
模块作用：实现Pauli CSS码的逻辑算符推导与若干标准实例（Steane、Surface），以及由线性码构造。
"""""
import numpy as np
from extendedstim.Code.QuantumCode.PauliCode import PauliCode
from extendedstim.Code.QuantumCode.QuantumCSSCode import QuantumCSSCode
from extendedstim.Physics.PauliOperator import PauliOperator
from extendedstim.tools.GaloisTools import orthogonalize, occupy


class PauliCSSCode(PauliCode, QuantumCSSCode):

    # %%  USER：构造方法
    def __init__(self, generators_x: list, generators_z: list, physical_number: int)->None:
        """""
        input.generators_x：X稳定子
        input.generators_z：Z稳定子
        input.physical_number：物理位数
        """""
        QuantumCSSCode.__init__(self, generators_x, generators_z, physical_number)

    # %%  USER：属性方法
    ##  TODO：求Pauli CSS code的距离（x方向）
    @property
    def distance_x(self):
        return 1

    ##  TODO：求Pauli CSS code的距离（z方向）
    @property
    def distance_z(self):
        return 1

    ##  TODO：求Pauli CSS code的逻辑算子（x方向）
    @property
    def logical_operators_x(self):
        if self._logical_operators_x is not None:
            return self._logical_operators_x
        else:
            matrix = self.check_matrix_x
            codewords = matrix.null_space()
            independent_null_basis_list = []
            for vec in codewords:
                rank_before = np.linalg.matrix_rank(matrix)
                matrix = np.vstack([matrix, vec])
                if np.linalg.matrix_rank(matrix) == rank_before + 1:
                    independent_null_basis_list.append(vec)
            basis_list = orthogonalize(independent_null_basis_list)
            pauli_logical_operators_x = []
            pauli_logical_operators_z = []
            for i in range(len(basis_list)):
                occupy_temp = occupy(basis_list[i])
                temp = PauliOperator.HermitianOperatorFromOccupy(occupy_temp, [])
                pauli_logical_operators_x.append(temp)
                temp = PauliOperator.HermitianOperatorFromOccupy([], occupy_temp)
                pauli_logical_operators_z.append(temp)
            self._logical_operators_x = np.array(pauli_logical_operators_x, dtype=PauliOperator)
            self._logical_operators_z = np.array(pauli_logical_operators_z, dtype=PauliOperator)
            return self._logical_operators_x

    ##  TODO：求Pauli CSS code的逻辑算子（z方向）
    @property
    def logical_operators_z(self):
        if self._logical_operators_z is not None:
            return self._logical_operators_z
        else:
            _=self.logical_operators_x
            return self._logical_operators_z

    @staticmethod
    def SteaneCode():
        """""
        output：标准Steane (7,1,3) 的PauliCSSCode实例
        """""
        generators_x = [PauliOperator([3,4,5,6],[],1),PauliOperator([1,2,5,6],[],1),PauliOperator([0,2,4,6],[],1)]
        generators_z = [PauliOperator([],[3,4,5,6],1),PauliOperator([],[1,2,5,6],1),PauliOperator([],[0,2,4,6],1)]
        physical_number=7
        result=PauliCSSCode(generators_x, generators_z, physical_number)
        result._logical_operators_x=[PauliOperator([0,1,2],[],1)]
        result._logical_operators_z=[PauliOperator([],[0,1,2],1)]
        return result

    @staticmethod
    def SurfaceCode(d):
        """""
        input.d：奇数边长
        output：表面码实例 (仅d=3硬编码)
        """""
        generators_x=[]
        generators_z=[]
        if d==3:
            generators_x=[
                PauliOperator([6,7],[],1),
                PauliOperator([4,5,7,8],[],1),
                PauliOperator([0,1,3,4],[],1),
                PauliOperator([1,2],[],1)
            ]
            generators_z=[
                PauliOperator([],[3,4,6,7],1),
                PauliOperator([],[5,8],1),
                PauliOperator([],[0,3],1),
                PauliOperator([],[1,2,4,5],1)
            ]
            physical_number=9
            result=PauliCSSCode(generators_x, generators_z, physical_number)
            result._logical_operators_x=[PauliOperator([0,3,6],[],1)]
            result._logical_operators_z=[PauliOperator([],[0,1,2],1)]
        return result

    @staticmethod
    def FromLinearCode(linear_code):
        """""
        input.linear_code：LinearCode 实例
        output：PauliCSSCode 实例
        """""
        generators_x=[]
        generators_z=[]
        for i in range(linear_code.number_checker):
            occupy_temp = occupy(linear_code.check_matrix[i])
            generators_x.append(PauliOperator.HermitianOperatorFromOccupy(occupy_temp, []))
            generators_z.append(PauliOperator.HermitianOperatorFromOccupy([], occupy_temp))
        physical_number=linear_code.number_bit
        result=PauliCSSCode(generators_x, generators_z, physical_number)
        return result
