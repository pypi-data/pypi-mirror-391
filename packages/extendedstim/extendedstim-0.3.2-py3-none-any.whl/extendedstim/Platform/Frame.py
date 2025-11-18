"""""
模块作用：定义Pauli帧（Pauli Frame）模型，用于在Clifford电路模拟中跟踪误差传播，是`Platform`的简化/快速版本。
"""""
import galois
import numpy as np
from extendedstim.Physics.MajoranaOperator import MajoranaOperator
from extendedstim.Physics.PauliOperator import PauliOperator
from extendedstim.tools.TypingTools import isinteger


class Frame:
    GF=galois.GF(2)
    # %%  USER：===构造方法===
    def __init__(self):
        """""
        influence：初始化空帧，比特数和费米子位数为0。
        """""
        self.pauli_number=0
        self.majorana_number=0
        self.frame=None
        self.pauli_frame=None
        self.majorana_frame=None

    # %%  USER：===对象方法===
    ##  USER：---初始化平台，定义fermionic sites和qubits数目---
    def initialize(self, majorana_number, pauli_number):
        """""
        input.majorana_number：费米子位数
        input.pauli_number：量子位数
        influence：设置帧的大小并初始化为全零。
        """""

        ##  ---数据预处理---
        assert isinteger(majorana_number) and majorana_number>=0
        assert isinteger(pauli_number) and pauli_number>=0

        ##  ---定义平台初态---
        ##  定义平台qubits和fermionic sites分别的数目
        self.pauli_number=pauli_number
        self.majorana_number=majorana_number
        self.frame=self.GF(np.zeros(2*pauli_number+2*majorana_number,dtype=int))

    ##  USER：---强制初始化---
    def force(self, majorana_state:list[MajoranaOperator], pauli_state:list[PauliOperator]):
        """""
        input.majorana_state：Majorana稳定子列表
        input.pauli_state：Pauli稳定子列表
        influence：根据给定的稳定子随机初始化帧（模拟投影到随机的+1/-1本征态）。
        """""
        for stabilizer in range(len(majorana_state)):
            if np.random.rand()>0.5:
                self.frame[0:self.majorana_number*2]+=majorana_state[stabilizer].get_vector(self.majorana_number)
                self.frame[self.majorana_number*2:]+=pauli_state[stabilizer].get_vector(self.pauli_number)

    ##  USER：---测量算符op，返回测量结果，随机坍缩---
    def measure(self, op,reference_value):
        """""
        input.op：待测量的厄米算符
        input.reference_value：无噪声参考测量值 (+1或-1)
        output：int，实际测量结果 (+1或-1)
        influence：根据算符与当前帧的对易/反对易关系翻转参考值，并以50%概率更新帧。
        """""

        ##  ---数据预处理---
        assert op.is_hermitian
        assert reference_value==1 or reference_value==-1

        ##  ---测量算符op，返回测量结果，随机坍缩---
        if isinstance(op, MajoranaOperator):
            v0=op.get_vector(self.majorana_number)
            v1=self.frame[0:self.majorana_number*2]
            overlap_number=np.dot(v0,v1)
            weight_0=np.dot(v0,v0)
            weight_1=np.dot(v1,v1)
            if overlap_number+weight_0*weight_1==0:
                result=reference_value
            else:
                result=-reference_value
            if np.random.rand()>0.5:
                self.frame[0:self.majorana_number*2]+=v0
            return result
        elif isinstance(op, PauliOperator):
            v0=op.get_vector(self.pauli_number)
            v0_x=v0[0::2]
            v0_z=v0[1::2]
            v1=self.frame[self.majorana_number*2:]
            v1_x=v1[0::2]
            v1_z=v1[1::2]
            overlap_number=np.dot(v0_x,v1_z)+np.dot(v0_z,v1_x)
            if overlap_number==0:
                result=reference_value
            else:
                result=-reference_value
            if np.random.rand()>0.5:
                self.frame[self.majorana_number*2:]+=v0
            return result
        else:
            raise ValueError

    ##  USER：---X门，作用于qubit_index---
    def x(self, qubit_index: int):
        """""
        input.qubit_index：目标量子位
        influence：在Pauli帧模型中，理想的单比特门不改变误差帧，因此为空操作。
        """""
        pass

    ##  USER：---Y门，作用于qubit_index---
    def y(self, qubit_index: int):
        """""
        input.qubit_index：目标量子位
        influence：理想门，空操作。
        """""
        pass

    ##  USER：---Z门，作用于qubit_index---
    def z(self, qubit_index: int):
        """""
        input.qubit_index：目标量子位
        influence：理想门，空操作。
        """""
        pass


    ##  USER：---Hadamard gate，作用于qubit_index---
    def h(self, qubit_index: int):
        """""
        input.qubit_index：目标量子位
        influence：交换Pauli帧中对应量子位的X和Z分量。
        """""
        ##  ----数据预处理----
        assert isinteger(qubit_index) and 0<=qubit_index<self.pauli_number
        qubit_index_x=self.majorana_number*2+qubit_index*2
        qubit_index_z=self.majorana_number*2+qubit_index*2+1

        ##  ----交换----
        cache=self.frame[qubit_index_x]
        self.frame[qubit_index_x]=self.frame[qubit_index_z]
        self.frame[qubit_index_z]=cache

    ##  USER：---S门，作用于pauli_index---
    def s(self, pauli_index: int):
        """""
        input.pauli_index：目标量子位
        influence：在Pauli帧中，Z分量加上X分量 (Z -> ZX)。
        """""

        ##  ---数据预处理---
        assert isinteger(pauli_index) and 0<=pauli_index<self.pauli_number
        qubit_index_x=self.majorana_number*2+pauli_index*2
        qubit_index_z=self.majorana_number*2+pauli_index*2+1

        ##  ----S门作用----
        self.frame[qubit_index_z]+=self.frame[qubit_index_x]

    ##  USER：---gamma门，作用于majorana_index---
    def u(self, majorana_index: int):
        """""
        input.majorana_index：目标费米子位
        influence：理想门，空操作。
        """""
        pass

    ##  USER：---gamma_prime门，作用于majorana_index---
    def v(self, majorana_index: int):
        """""
        input.majorana_index：目标费米子位
        influence：理想门，空操作。
        """""
        pass

    ##  USER：---i*gamma*gamma_prime门，作用于majorana_index---
    def n(self, majorana_index: int):
        """""
        input.majorana_index：目标费米子位
        influence：理想门，空操作。
        """""
        pass

    ##  USER：---P门，作用于majorana_index---
    def p(self, majorana_index: int):
        """""
        input.majorana_index：目标费米子位
        influence：交换费米子帧中对应位的X和Z分量。
        """""

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0<=majorana_index<self.majorana_number
        majorana_index_x=majorana_index*2
        majorana_index_z=majorana_index*2+1

        ##  ---P门作用---
        cache=self.frame[majorana_index_x]
        self.frame[majorana_index_x]=self.frame[majorana_index_z]
        self.frame[majorana_index_z]=cache

    ##  USER：---CNOT门，作用于control_index,target_index，两者是qubits，前者是控制位---
    def cx(self, control_index, target_index):
        """""
        input.control_index, target_index：控制和目标量子位
        influence：更新Pauli帧：target_X += control_X, control_Z += target_Z。
        """""

        ##  ---数据预处理---
        assert isinteger(control_index) and 0<=control_index<self.pauli_number
        assert isinteger(target_index) and 0<=target_index<self.pauli_number
        control_qubit_index_x=self.majorana_number*2+control_index*2
        control_qubit_index_z=self.majorana_number*2+control_index*2+1
        target_qubit_index_x=self.majorana_number*2+target_index*2
        target_qubit_index_z=self.majorana_number*2+target_index*2+1

        ##  ---CNOT门作用---
        self.frame[target_qubit_index_x]+=self.frame[control_qubit_index_x]
        self.frame[control_qubit_index_z]+=self.frame[target_qubit_index_z]

    ##  USER：---CN-NOT门，作用于control_index,target_index，前者是fermionic site控制位，后者是qubit目标位---
    def cnx(self, control_index, target_index):
        """""
        input.control_index：费米子控制位
        input.target_index：量子位目标
        influence：根据混合门规则更新费米子-量子位帧。
        """""

        ##  ---数据预处理---
        assert isinteger(control_index) and 0<=control_index<self.majorana_number
        assert isinteger(target_index) and 0<=target_index<self.pauli_number
        control_majorana_index_x=control_index*2
        control_majorana_index_z=control_index*2+1
        target_qubit_index_x=self.majorana_number*2+target_index*2
        target_qubit_index_z=self.majorana_number*2+target_index*2+1

        target_x= self.frame[target_qubit_index_x]+self.frame[control_majorana_index_x]+self.frame[control_majorana_index_z]
        control_x=self.frame[control_majorana_index_x]+self.frame[target_qubit_index_z]
        control_z=self.frame[control_majorana_index_z]+self.frame[target_qubit_index_z]
        self.frame[target_qubit_index_x]=target_x
        self.frame[control_majorana_index_x]=control_x
        self.frame[control_majorana_index_z]=control_z

    ##  USER：---CN-N门，作用于control_index,target_index，前者是fermionic site控制位，后者是fermionic site目标位---
    def cnn(self, control_index, target_index):
        """""
        input.control_index, target_index：控制和目标费米子位
        influence：根据费米子门规则更新帧。
        """""

        ##  ---数据预处理---
        assert isinteger(control_index) and 0<=control_index<self.majorana_number
        assert isinteger(target_index) and 0<=target_index<self.majorana_number
        control_majorana_index_x=control_index*2
        control_majorana_index_z=control_index*2+1
        target_majorana_index_x=target_index*2
        target_majorana_index_z=target_index*2+1

        control_x= self.frame[control_majorana_index_x]+self.frame[target_majorana_index_x]+self.frame[target_majorana_index_z]
        control_z= self.frame[control_majorana_index_z]+self.frame[target_majorana_index_x]+self.frame[target_majorana_index_z]
        target_x= self.frame[target_majorana_index_x]+self.frame[control_majorana_index_x]+self.frame[control_majorana_index_z]
        target_z= self.frame[target_majorana_index_z]+self.frame[control_majorana_index_x]+self.frame[control_majorana_index_z]
        self.frame[control_majorana_index_x]=control_x
        self.frame[control_majorana_index_z]=control_z
        self.frame[target_majorana_index_x]=target_x
        self.frame[target_majorana_index_z]=target_z

    ##  USER：---Braid门，前者是fermionic site控制位，后者是fermionic site目标位---
    def braid(self, control_index, target_index, *args):
        """""
        input.control_index, target_index：费米子位
        influence：交换费米子帧中的特定分量。
        """""

        ##  ---数据预处理---
        assert isinteger(control_index) and 0<=control_index<self.majorana_number
        assert isinteger(target_index) and 0<=target_index<self.majorana_number
        control_majorana_index_z=control_index*2+1
        target_majorana_index_x=target_index*2

        cache=self.frame[control_majorana_index_z]
        self.frame[control_majorana_index_z]=self.frame[target_majorana_index_x]
        self.frame[target_majorana_index_x]=cache

    ##  USER：---执行pauli_index上的X-error---
    def x_error(self, pauli_index, p):
        """""
        input.pauli_index：目标量子位
        input.p：错误概率
        influence：以概率p在帧上施加一个X错误。
        """""
        if np.random.rand()<p:
            qubit_index_x=self.majorana_number*2+pauli_index*2
            self.frame[qubit_index_x]+=self.GF(1)

    ##  USER：---执行pauli_index上的Y-error---
    def y_error(self, pauli_index, p):
        """""
        input.pauli_index：目标量子位
        input.p：错误概率
        influence：以概率p在帧上施加一个Y错误 (X和Z)。
        """""
        if np.random.rand()<p:
            qubit_index_x=self.majorana_number*2+pauli_index*2
            qubit_index_z=self.majorana_number*2+pauli_index*2+1
            self.frame[qubit_index_x]+=self.GF(1)
            self.frame[qubit_index_z]+=self.GF(1)

    ##  USER：---执行pauli_index上的Z-error---
    def z_error(self, pauli_index, p):
        """""
        input.pauli_index：目标量子位
        input.p：错误概率
        influence：以概率p在帧上施加一个Z错误。
        """""
        if np.random.rand()<p:
            qubit_index_z=self.majorana_number*2+pauli_index*2+1
            self.frame[qubit_index_z]+=self.GF(1)

    ##  USER：---执行majorana_index上的U-error---
    def u_error(self, majorana_index, p):
        """""
        input.majorana_index：目标费米子位
        input.p：错误概率
        influence：以概率p在帧上施加一个U (X-like) 错误。
        """""
        if np.random.rand()<p:
            majorana_index_x=majorana_index*2
            self.frame[majorana_index_x]+=self.GF(1)

    ##  USER：---执行majorana_index上的V-error---
    def v_error(self, majorana_index, p):
        """""
        input.majorana_index：目标费米子位
        input.p：错误概率
        influence：以概率p在帧上施加一个V (Z-like) 错误。
        """""
        if np.random.rand()<p:
            majorana_index_z=majorana_index*2+1
            self.frame[majorana_index_z]+=self.GF(1)

    ##  USER：---执行majorana_index上的N-error---
    def n_error(self, majorana_index, p):
        """""
        input.majorana_index：目标费米子位
        input.p：错误概率
        influence：以概率p在帧上施加一个N (Y-like) 错误。
        """""
        if np.random.rand()<p:
            majorana_index_x=majorana_index*2
            majorana_index_z=majorana_index*2+1
            self.frame[majorana_index_x]+=self.GF(1)
            self.frame[majorana_index_z]+=self.GF(1)

    ##  USER：---将系统在pauli_index上重置为0态---
    def reset(self, pauli_index):
        """""
        input.pauli_index：目标量子位
        influence：将帧中对应量子位分量清零，并随机引入一个Z错误（模拟测量后重置）。
        """""

        ##  ---数据预处理---
        assert isinteger(pauli_index) and 0<=pauli_index<self.pauli_number
        qubit_index_x=self.majorana_number*2+pauli_index*2
        qubit_index_z=self.majorana_number*2+pauli_index*2+1

        ##  ----重置0态----
        self.frame[qubit_index_x]=0
        self.frame[qubit_index_z]=0
        if np.random.rand()<0.5:
            self.frame[qubit_index_z]=self.GF(1)

    ##  USER：---将系统在majorana_index上重置为空态---
    def fermionic_reset(self, majorana_index):
        """""
        input.majorana_index：目标费米子位
        influence：将帧中对应费米子位分量清零，并随机引入一个N错误（模拟测量后重置）。
        """""

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0<=majorana_index<self.majorana_number
        majorana_index_x=majorana_index*2
        majorana_index_z=majorana_index*2+1
        self.frame[majorana_index_x]=self.GF(0)
        self.frame[majorana_index_z]=self.GF(0)

        ##  ---重置空态---
        if np.random.rand()<0.5:
            self.frame[majorana_index_z]=self.GF(1)
            self.frame[majorana_index_x]=self.GF(1)
