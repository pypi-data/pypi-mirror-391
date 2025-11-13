"""""
模块作用：实现Pauli稳定子码的基础属性与从校验矩阵构造。
"""""
import numpy as np
from extendedstim.Code.QuantumCode.QuantumCode import QuantumCode
from extendedstim.Physics.MajoranaOperator import MajoranaOperator


class PauliCode(QuantumCode):

    # %%  USER：构造方法
    def __init__(self, generators, physical_number):
        """""
        input.generators：Pauli/等价表示生成元
        input.physical_number：qubits数
        """""
        super().__init__(generators, physical_number)

    # %%  USER：属性方法
    ##  TODO：求Pauli code的距离
    @property
    def distance(self):
        return 1

    ##  TODO：求Pauli code的逻辑算子
    @property
    def logical_operators(self):
        return []

    # %%  USER：静态方法
    ##  USER：基于校验矩阵构造code
    @staticmethod
    def FromCheckMatrix(check_matrix):
        """""
        input.check_matrix：GF(2) (m,2n)
        output：PauliCode 实例
        """""
        generators = np.empty(check_matrix.shape[0], dtype=MajoranaOperator)
        for temp in range(check_matrix.shape[0]):
            occupy_x = np.where(check_matrix[temp, 0::2] == 1)
            occupy_z = np.where(check_matrix[temp, 1::2] == 1)
            generators[temp] = MajoranaOperator.HermitianOperatorFromOccupy(occupy_x, occupy_z)
        physical_number = check_matrix.shape[1] // 2
        return PauliCode(generators, physical_number)
