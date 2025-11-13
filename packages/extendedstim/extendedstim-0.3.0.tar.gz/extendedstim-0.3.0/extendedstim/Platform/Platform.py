"""""
模块作用：定义基于稳定子表述的平台态演化与测量模型，支持Pauli与Majorana门、噪声、测量与复位。
"""""
import copy
from extendedstim.Physics.MajoranaOperator import MajoranaOperator
from extendedstim.Physics.PauliOperator import PauliOperator
from extendedstim.tools.GaloisTools import *
from extendedstim.tools.TypingTools import isinteger


class Platform:
    GF=galois.GF(2)
    # %%  USER：===构造方法===
    def __init__(self):
        self.pauli_number = 0
        self.majorana_number = 0
        self.stabilizers_pauli = []
        self.stabilizers_majorana = []
        self.stabilizers=None
        self.coffs=None

    # %%  USER：===对象方法===
    ##  USER：---初始化平台，定义fermionic sites和qubits数目---
    def initialize(self, majorana_number, pauli_number):
        """""
        input.majorana_number：费米子位数
        input.pauli_number：量子位数
        """""

        ##  ---数据预处理---
        assert isinteger(majorana_number) and majorana_number >= 0
        assert isinteger(pauli_number) and pauli_number >= 0

        ##  ---定义平台初态---
        ##  定义平台qubits和fermionic sites分别的数目
        self.pauli_number = pauli_number
        self.majorana_number = majorana_number
        self.stabilizers=self.GF(np.zeros((majorana_number+pauli_number,2*majorana_number+2*pauli_number),dtype=int))
        self.coffs=np.ones(majorana_number+pauli_number,dtype=complex)

        ##  初始化状态，平台处于完全混态
        for i in range(majorana_number):
            if np.random.rand() < 0.5:
                self.stabilizers_majorana.append(MajoranaOperator([i], [i], 1j))
            else:
                self.stabilizers_majorana.append(MajoranaOperator([i], [i], -1j))
                self.coffs[i]=-1
            self.stabilizers_pauli.append(PauliOperator([], [], 1))
        for i in range(pauli_number):
            if np.random.rand() < 0.5:
                self.stabilizers_pauli.append(PauliOperator([], [i], 1))
            else:
                self.stabilizers_pauli.append(PauliOperator([], [i], -1))
                self.coffs[i+majorana_number]=-1
            self.stabilizers_majorana.append(MajoranaOperator([], [], 1))

    ##  USER：---强制初始化---
    def force(self,majorana_state,pauli_state):
        """""
        input.majorana_state：列表[MajoranaOperator]
        input.pauli_state：列表[PauliOperator]
        influence：覆盖平台稳定子到给定状态
        """""
        self.stabilizers_majorana = copy.deepcopy(majorana_state)
        self.stabilizers_pauli = copy.deepcopy(pauli_state)
        for i in range(len(majorana_state)):
            v_majorana = majorana_state[i].get_vector(self.majorana_number)
            v_pauli = pauli_state[i].get_vector(self.pauli_number)
            self.stabilizers[i,0:self.majorana_number*2]=v_majorana
            self.stabilizers[i,self.majorana_number*2:]=v_pauli

    ##  USER：----测量算符op，返回测量结果，随机坍缩----
    def measure(self,op):
        """""
        input.op：PauliOperator 或 MajoranaOperator（厄米）
        output：+1 或 -1 测量结果
        influence：更新稳定子组或一致性检查
        """""

        ##  ---数据预处理---
        assert op.is_hermitian
        if isinstance(op, MajoranaOperator):
            vector_op=np.append(op.get_vector(self.majorana_number),self.GF.Zeros(self.pauli_number*2))
        else:
            vector_op=np.append(self.GF.Zeros(self.majorana_number*2),op.get_vector(self.pauli_number))
        first_index=None
        for i in range(len(self.stabilizers)):
            pauli_commute=(np.dot(self.stabilizers[i][self.majorana_number*2::2],vector_op[self.majorana_number*2+1::2])+
                           np.dot(self.stabilizers[i][self.majorana_number*2+1::2],vector_op[self.majorana_number*2::2]))
            majorana_commute=(np.dot(self.stabilizers[i][0:self.majorana_number*2],vector_op[0:self.majorana_number*2])+
                              np.sum(vector_op[0:self.majorana_number*2])*np.sum(self.stabilizers[i][0:self.majorana_number*2]))

            if majorana_commute+pauli_commute==0 and first_index is None:
                first_index=i
            elif majorana_commute+pauli_commute==0 and first_index is not None:
                self.stabilizers[i]+=self.stabilizers[first_index]
            else:
                pass
        if first_index is not None:
            if np.random.rand() < 0.5:
                self.stabilizers[first_index]=vector_op
                self.coffs[first_index]=op.coff
                return 1
            else:
                self.stabilizers[first_index]=-vector_op
                self.coffs[first_index]=-op.coff
                return -1
        else:
            solution=solve(self.stabilizers,vector_op)
            coff=np.prod([self.coffs[i] for i in range(len(self.stabilizers)) if solution[i]==1])
            if coff==op.coff:
                return 1
            else:
                return -1

    ##  USER：---X门，作用于qubit_index---
    def x(self, qubit_index: int):
        """""
        input.qubit_index：目标量子位
        influence：翻转与Z重叠的稳定子相位
        """""

        ##  ---数据预处理---
        assert isinteger(qubit_index) and 0 <= qubit_index < self.pauli_number

        ##  ---X门作用---
        indices=np.where(self.stabilizers[:,self.majorana_number*2+qubit_index*2+1]==1)[0]
        self.coffs[indices]=-self.coffs[indices]

    ##  USER：----Y门，作用于qubit_index----
    def y(self, qubit_index: int):
        """""
        input.qubit_index：目标量子位
        influence：对X与Z重叠稳定子均翻相
        """""

        ##  ---数据预处理---
        assert isinteger(qubit_index) and 0 <= qubit_index < self.pauli_number

        ##  ---Y门作用---
        indices_x=np.where(self.stabilizers[:,self.majorana_number*2+qubit_index*2+1]==1)[0]
        self.coffs[indices_x]=-self.coffs[indices_x]
        indices_z=np.where(self.stabilizers[:,self.majorana_number*2+qubit_index*2]==1)[0]
        self.coffs[indices_z]=-self.coffs[indices_z]

    ##  USER：---Z门，作用于qubit_index---
    def z(self, qubit_index: int):
        """""
        input.qubit_index：目标量子位
        influence：翻转与X重叠的稳定子相位
        """""

        ##  ---数据预处理---
        assert isinteger(qubit_index) and 0 <= qubit_index < self.pauli_number

        ##  ----Z门作用----
        indices=np.where(self.stabilizers[:,self.majorana_number*2+qubit_index*2]==1)[0]
        self.coffs[indices]=-self.coffs[indices]

    ##  USER：---Hadamard gate，作用于qubit_index---
    def h(self, qubit_index: int):
        """""
        input.qubit_index：目标量子位
        influence：交换X/Z支撑，更新相位
        """""

        ##  ---数据预处理---
        assert isinteger(qubit_index) and 0 <= qubit_index < self.pauli_number

        ##  ---Hadamard门作用---
        indices=np.where(self.stabilizers[:,self.majorana_number*2+qubit_index*2+1]==1==self.stabilizers[:,self.majorana_number*2+qubit_index*2])[0]
        self.coffs[indices]=-self.coffs[indices]
        caches=self.stabilizers[:,self.majorana_number*2+qubit_index*2]
        self.stabilizers[:,self.majorana_number*2+qubit_index*2]=self.stabilizers[:,self.majorana_number*2+qubit_index*2+1]
        self.stabilizers[:,self.majorana_number*2+qubit_index*2+1]=caches

    ##  USER：---S门，作用于pauli_index---
    def s(self, pauli_index: int):
        """""
        input.pauli_index：目标量子位
        influence：Z += X（相位门）
        """""

        ##  ---数据预处理---
        assert isinteger(pauli_index) and 0 <= pauli_index < self.pauli_number

        ##  ---S门作用---
        indices=np.where(self.stabilizers[:,self.majorana_number*2+pauli_index*2]==1)[0]
        self.coffs[indices]=1j*self.coffs[indices]
        self.stabilizers[:,self.majorana_number*2+pauli_index*2+1]+=self.stabilizers[:,self.majorana_number*2+pauli_index*2]

    ##  USER：---gamma门，作用于majorana_index---
    def u(self, majorana_index: int):
        """""
        input.majorana_index：目标费米子位
        influence：依据重叠权重翻相
        """""

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---gamma门作用---
        weights=np.sum(self.stabilizers,axis=1)
        overlaps=self.GF(np.where(self.stabilizers[:,majorana_index*2]==1,1,0))
        indices=np.where(weights+overlaps==0)[0]
        self.coffs[indices]=-self.coffs[indices]

    ##  USER：---gamma_prime门，作用于majorana_index---
    def v(self, majorana_index: int):
        """""
        input.majorana_index：目标费米子位
        influence：依据Z重叠翻相
        """""
        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---gamma_prime门作用---
        weights=np.sum(self.stabilizers,axis=1)
        overlaps=np.where(self.stabilizers[:,majorana_index*2+1]==1,1,0)
        indices=np.where(weights+overlaps==0)[0]
        self.coffs[indices]=-self.coffs[indices]

    ##  USER：---i*gamma*gamma_prime门，作用于majorana_index---
    def n(self, majorana_index: int):
        """""
        input.majorana_index：目标费米子位
        influence：依据X或Z奇偶翻相
        """""
        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---i*gamma*gamma_prime门作用---
        weights=np.sum(self.stabilizers,axis=1)
        overlaps=self.GF(np.where(np.logical_xor(self.stabilizers[:,majorana_index*2]==1,self.stabilizers[:,majorana_index*2+1]==1),1,0))
        indices=np.where(weights+overlaps==0)[0]
        self.coffs[indices]=-self.coffs[indices]

    ##  USER：----P门，作用于majorana_index----
    def p(self, majorana_index: int):
        """""
        input.majorana_index：目标费米子位
        influence：交换X/Z支撑
        """""

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---P门作用---
        indices=np.where(np.logical_and(self.stabilizers[:,majorana_index*2+1]==1,self.stabilizers[:,majorana_index*2]==0))[0]
        self.coffs[indices]=-self.coffs[indices]
        caches=self.stabilizers[:,majorana_index*2]
        self.stabilizers[:,majorana_index*2]=self.stabilizers[:,majorana_index*2+1]
        self.stabilizers[:,majorana_index*2+1]=caches

    ##  USER：---CNOT门，作用于control_index,target_index，两者是qubits，前者是控制位---
    def cx(self, control_index, target_index):
        """""
        input.control_index,target_index：量子位索引
        influence：稳定子线性变换（X/Z互相传播）
        """""

        ##  ---数据预处理---
        assert isinteger(control_index) and 0 <= control_index < self.pauli_number
        assert isinteger(target_index) and 0 <= target_index < self.pauli_number

        ##  ---CNOT门作用---
        control_qubit_index_x=control_index*2+self.majorana_number*2
        control_qubit_index_z=control_index*2+1+self.majorana_number*2
        target_qubit_index_x=target_index*2+self.majorana_number*2
        target_qubit_index_z=target_index*2+1+self.majorana_number*2
        targets_x=self.stabilizers[:,control_qubit_index_x]+self.stabilizers[:,target_qubit_index_x]
        control_z=self.stabilizers[:,control_qubit_index_z]+self.stabilizers[:,target_qubit_index_z]
        self.stabilizers[:,target_qubit_index_x]=targets_x
        self.stabilizers[:,target_qubit_index_z]=control_z

    ##  USER：---CN-NOT门，作用于control_index,target_index，前者是fermionic site控制位，后者是qubit目标位---
    def cnx(self, control_index, target_index):
        """""
        input.control_index：费米子控制位
        input.target_index：量子位目标
        influence：见文档推导的稳定子更新规则
        """""

        ##  USER：----数据预处理----
        assert isinteger(control_index) and 0 <= control_index < self.majorana_number
        assert isinteger(target_index) and 0 <= target_index < self.pauli_number

        ##  USER：----处理过程----
        control_majorana_index_x=control_index*2
        control_majorana_index_z=control_index*2+1
        target_qubit_index_x=self.majorana_number*2+target_index*2
        target_qubit_index_z=self.majorana_number*2+target_index*2+1

        targets_x= self.stabilizers[:,target_qubit_index_x]+self.stabilizers[:,control_majorana_index_x]+self.stabilizers[:,control_majorana_index_z]
        controls_x=self.stabilizers[:,control_majorana_index_x]+self.stabilizers[:,target_qubit_index_z]
        controls_z=self.stabilizers[:,control_majorana_index_z]+self.stabilizers[:,target_qubit_index_z]
        indices=np.where(self.stabilizers[:,target_qubit_index_z]+self.stabilizers[:,control_majorana_index_x]+self.stabilizers[:,control_majorana_index_z]==1)[0]
        self.coffs[indices]=-self.coffs[indices]
        self.stabilizers[:,target_qubit_index_x]=targets_x
        self.stabilizers[:,control_majorana_index_x]=controls_x
        self.stabilizers[:,control_majorana_index_z]=controls_z

        ##  USER：----结果返回----
        return None

    ##  USER：---CN-N门，作用于control_index,target_index，前者是fermionic site控制位，后者是fermionic site目标位---
    def cnn(self, control_index, target_index):
        """""
        input.control_index,target_index：费米子索引
        influence：见文档推导的稳定子更新规则
        """""

        ##  USER：----数据预处理----
        assert isinteger(control_index) and 0<=control_index<self.majorana_number
        assert isinteger(target_index) and 0<=target_index<self.majorana_number
        control_majorana_index_x=control_index*2
        control_majorana_index_z=control_index*2+1
        target_majorana_index_x=target_index*2
        target_majorana_index_z=target_index*2+1

        ##  USER：----处理过程----
        indices=np.where(
            np.logical_xor(
                np.logical_and(
                    np.logical_xor(self.stabilizers[:,control_majorana_index_x]==1,self.stabilizers[:,control_majorana_index_z]==1),
                    np.logical_xor(self.stabilizers[:,target_majorana_index_x]==1,self.stabilizers[:,target_majorana_index_z]==1)),
                np.logical_and(
                    np.logical_xor(self.stabilizers[:, target_majorana_index_x]==1, self.stabilizers[:, target_majorana_index_z]==1),
                    np.logical_xor(self.stabilizers[:, control_majorana_index_x]==1, self.stabilizers[:, control_majorana_index_z]==1))
        ))[0]
        self.coffs[indices]=-self.coffs[indices]
        control_x= self.stabilizers[:,control_majorana_index_x]+self.stabilizers[:,target_majorana_index_x]+self.stabilizers[:,target_majorana_index_z]
        control_z= self.stabilizers[:,control_majorana_index_z]+self.stabilizers[:,target_majorana_index_x]+self.stabilizers[:,target_majorana_index_z]
        target_x= self.stabilizers[:,target_majorana_index_x]+self.stabilizers[:,control_majorana_index_x]+self.stabilizers[:,control_majorana_index_z]
        target_z= self.stabilizers[:,target_majorana_index_z]+self.stabilizers[:,control_majorana_index_x]+self.stabilizers[:,control_majorana_index_z]
        self.stabilizers[:,control_majorana_index_x]=control_x
        self.stabilizers[:,control_majorana_index_z]=control_z
        self.stabilizers[:,target_majorana_index_x]=target_x
        self.stabilizers[:,target_majorana_index_z]=target_z

        ##  USER：----结果返回----
        return None

    ##  USER：---Braid门，前者是fermionic site控制位，后者是fermionic site目标位---
    def braid(self,control_index,target_index,*args):
        """""
        input.control_index,target_index：费米子索引
        influence：交换特定支撑并翻相
        """""
        ##  ---数据预处理---
        assert isinteger(control_index) and 0<=control_index<self.majorana_number
        assert isinteger(target_index) and 0<=target_index<self.majorana_number
        control_majorana_index_z=control_index*2+1
        target_majorana_index_x=target_index*2
        indices=np.where(np.logical_and(self.stabilizers[:,control_majorana_index_z]==0,self.stabilizers[:,target_majorana_index_x]==1))[0]
        self.coffs[indices]=-self.coffs[indices]
        caches=self.stabilizers[:,control_majorana_index_z]
        self.stabilizers[:,control_majorana_index_z]=self.stabilizers[:,target_majorana_index_x]
        self.stabilizers[:,target_majorana_index_x]=caches

    ##  USER：---执行pauli_index上的X-error---
    def x_error(self, pauli_index, p):
        if np.random.rand() < p:
            self.x(pauli_index)

    ##  USER：---执行pauli_index上的Y-error---
    def y_error(self, pauli_index, p):
        if np.random.rand() < p:
            self.y(pauli_index)

    ##  USER：---执行pauli_index上的Z-error---
    def z_error(self, pauli_index, p):
        if np.random.rand() < p:
            self.z(pauli_index)

    ##  USER：---执行majorana_index上的U-error---
    def u_error(self, majorana_index, p):
        if np.random.rand() < p:
            self.u(majorana_index)

    ##  USER：---执行majorana_index上的V-error---
    def v_error(self, majorana_index, p):
        if np.random.rand() < p:
            self.v(majorana_index)

    ##  USER：---执行majorana_index上的N-error---
    def n_error(self, majorana_index, p):
        if np.random.rand() < p:
            self.n(majorana_index)

    ##  USER：---将系统在pauli_index上重置为0态---
    def reset(self, pauli_index):
        """""
        input.pauli_index：目标量子位
        influence：将对应稳定子行设置为Z=+1
        """""

        ##  ---数据预处理---
        assert isinteger(pauli_index) and 0 <= pauli_index < self.pauli_number

        ##  ---重置0态---
        vector_op=np.append(self.GF.Zeros(self.majorana_number*2), PauliOperator([],[pauli_index],1).get_vector(self.pauli_number))
        first_index=None
        for i in range(len(self.stabilizers)):
            pauli_commute=(np.dot(self.stabilizers[i][self.majorana_number*2::2], vector_op[self.majorana_number*2+1::2])+
                           np.dot(self.stabilizers[i][self.majorana_number*2+1::2], vector_op[self.majorana_number*2::2]))
            majorana_commute=(np.dot(self.stabilizers[i][0:self.majorana_number*2], vector_op[0:self.majorana_number*2])+
                              np.sum(vector_op[0:self.majorana_number*2])*np.sum(self.stabilizers[i][0:self.majorana_number*2]))

            if majorana_commute+pauli_commute==0 and first_index is None:
                first_index=i
            elif majorana_commute+pauli_commute==0 and first_index is not None:
                self.stabilizers[i]+=self.stabilizers[first_index]
            else:
                pass
        if first_index is not None:
            self.stabilizers[first_index]=vector_op
            self.coffs[first_index]=1
        else:
            solution=solve(self.stabilizers, vector_op)
            coff=np.prod([self.coffs[i] for i in range(len(self.stabilizers)) if solution[i]==1])
            index_first_one=np.where(solution==1)[0][0]
            if coff==-1:
                self.stabilizers[index_first_one]=vector_op
                self.coffs[index_first_one]=1


    ##  USER：---将系统在majorana_index上重置为空态---
    def fermionic_reset(self, majorana_index):
        """""
        input.majorana_index：目标费米子位
        influence：将对应稳定子行设置为N=+1
        """""

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---重置空态---
        vector_op=np.append(MajoranaOperator([],[majorana_index],1).get_vector(self.majorana_number),self.GF.Zeros(self.pauli_number*2))
        first_index=None
        for i in range(len(self.stabilizers)):
            pauli_commute=(np.dot(self.stabilizers[i][self.majorana_number*2::2], vector_op[self.majorana_number*2+1::2])+
                           np.dot(self.stabilizers[i][self.majorana_number*2+1::2], vector_op[self.majorana_number*2::2]))
            majorana_commute=(np.dot(self.stabilizers[i][0:self.majorana_number*2], vector_op[0:self.majorana_number*2])+
                              np.sum(vector_op[0:self.majorana_number*2])*np.sum(self.stabilizers[i][0:self.majorana_number*2]))

            if majorana_commute+pauli_commute==0 and first_index is None:
                first_index=i
            elif majorana_commute+pauli_commute==0 and first_index is not None:
                self.stabilizers[i]+=self.stabilizers[first_index]
            else:
                pass
        if first_index is not None:
            self.stabilizers[first_index]=vector_op
            self.coffs[first_index]=1
        else:
            solution=solve(self.stabilizers, vector_op)
            coff=np.prod([self.coffs[i] for i in range(len(self.stabilizers)) if solution[i]==1])
            index_first_one=np.where(solution==1)[0][0]
            if coff==-1:
                self.stabilizers[index_first_one]=vector_op
                self.coffs[index_first_one]=1
