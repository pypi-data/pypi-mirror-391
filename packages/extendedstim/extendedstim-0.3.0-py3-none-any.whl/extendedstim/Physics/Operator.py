"""""
模块作用：定义抽象的量子算符基类，统一占据表示、系数、基本代数操作接口。
"""""
from abc import abstractmethod, ABC
import galois
import numpy as np
from extendedstim.tools.TypingTools import isinteger, islist


class Operator(ABC):
    __slots__ = ['occupy_x', 'occupy_z', 'coff']

    #%%  USER：===构造方法===
    def __init__(self, occupy_x:list[int]|np.ndarray,
                 occupy_z:list[int]|np.ndarray,
                 coff:complex|float|int):
        """""
        input.occupy_x: 占据x轴的量子位索引列表
        input.occupy_z: 占据z轴的量子位索引列表
        input.coff: 系数 (±1, ±i)
        output：无（构造对象）
        示例：$-i\\hat X_0\\hat X_2\\hat Z_3\\hat X_3\\hat Z_3$ 记为
        op = Operator([0, 2, 3], [2, 3], -1j)
        """""
        assert islist(occupy_x)
        assert islist(occupy_z)
        assert coff==1 or coff==-1 or coff==1j or coff==-1j
        self.occupy_x = np.array(occupy_x, dtype=int)
        self.occupy_z = np.array(occupy_z, dtype=int)
        self.occupy_x.sort()
        self.occupy_z.sort()
        self.coff = coff

    #%%  USER：===重载运算符===
    ##  USER：----矩阵乘法----
    @abstractmethod
    def __matmul__(self, other):
        """""
        input.other：另一个同类型算符
        output：乘积算符对象
        """""
        pass

    ##  USER：----右矩阵乘法----
    @abstractmethod
    def __rmatmul__(self, other):
        """""
        input.other：左操作数
        output：乘积算符
        """""
        pass

    ##  USER：----左标量乘法----
    @abstractmethod
    def __mul__(self, other):
        """""
        input.other：系数 (±1, ±i)
        output：新算符（系数被放缩）
        """""
        pass

    ##  USER：----右标量乘法----
    @abstractmethod
    def __rmul__(self, other):
        """""
        input.other：系数 (±1, ±i)
        output：新算符
        """""
        pass

    ##  USER：----字符串表示----
    @abstractmethod
    def __str__(self):
        """""
        output：str，可读表示
        """""
        pass

    ##  USER：----相等判断----
    @abstractmethod
    def __eq__(self, other):
        """""
        input.other：待比较对象
        output：bool，结构与系数均相等返回True
        """""
        pass

    ##  USER：----取负----
    @abstractmethod
    def __neg__(self):
        """""
        output：新算符，对系数取负号
        """""
        pass

    #%%  USER：===属性方法===
    ##  USER：----算符的权重----
    @property
    def weight(self)->int:
        """""
        output：占据x轴和z轴的量子位索引的总数
        例如$-i\\hat X_0\\hat X_2\\hat Z_3\\hat X_3\\hat Z_3$的权重为5.
        如果将Y视为单个算符，请使用约化权重reduced_weight.
        """""
        return len(self.occupy_x) + len(self.occupy_z)

    ##  USER：----判断算符是否是厄米算符----
    @property
    @abstractmethod
    def is_hermitian(self)->bool:
        """""
        output：bool，是否满足厄米条件（与系数和占据相关）
        """""
        pass

    ##  USER：----求算符的对偶算符----
    @property
    @abstractmethod
    def dual(self):
        """""
        output：对偶算符（X/Z互换、保持系数规则）
        """""
        pass

    #%%  USER：===对象方法===
    ##  USER：----更换索引方式----
    @abstractmethod
    def index_map(self, index):

        ##  ----数据预处理----
        assert isinstance(index, np.ndarray) or isinstance(index, list)
        assert len(index) >= max(self.occupy_x.max(), self.occupy_z.max()) + 1

        ##  ----更换索引----
        x = np.array([index[i] for i in self.occupy_x], dtype=int)
        z = np.array([index[i] for i in self.occupy_z], dtype=int)

        ##  ----返回结果----
        return x, z, self.coff

    ##  USER：----获取向量表示----
    def get_vector(self, number:int)->galois.GF(2):
        """""
        input.number: 量子位的总数
        output：量子位的向量表示 (GF(2) 长度 2*number)
        例如$-i\\hat X_0\\hat X_2\\hat Z_3\\hat X_3\\hat Z_3$在4个量子位上的向量表示为[1,0,1,0,0,0,1,1].
        """""

        ##  ----数据预处理----
        assert isinteger(number)

        ##  ----构造向量----
        vector = galois.GF2(np.zeros(number * 2,dtype=int))
        vector[self.occupy_x * 2] = 1
        vector[self.occupy_z * 2 + 1] = 1

        ##  ----返回结果----
        return vector

    ##  USER：---复制算符---
    @abstractmethod
    def copy(self):
        """""
        output：同类型新对象，深复制占据与系数
        """""
        pass

    #%%  USER：静态方法
    ##  USER：---求多个算符的矩阵表示---
    @staticmethod
    def get_matrix(ops, number:int)->galois.GF(2):
        """""
        input.ops: 算符列表
        input.number: 指定量子位的总数
        output：算符的矩阵表示 (GF(2) shape=(len(ops),2*number))
        例如$-i\\hat X_0\\hat X_2$和$\\hat Z_1\\hat X_2\\hat Z_2$在3个qubits矩阵表示为
        """""
        ##  ----构造矩阵----
        matrix = None
        for i, op in enumerate(ops):
            vector = op.get_vector(number)
            if i == 0:
                matrix = vector
            else:
                matrix = np.vstack([matrix, vector])

        ##  ----返回结果----
        return matrix

    # %%  USER：静态方法
    ##  USER：---定义一个厄米算符，从占据处表示---
    @staticmethod
    @abstractmethod
    def HermitianOperatorFromOccupy(occupy_x, occupy_z):
        """""
        input.occupy_x：x占据索引
        input.occupy_z：z占据索引
        output：具体子类实例（厄米）
        """""
        pass

    ##  USER：---定义一个厄米算符，从向量表示---
    @staticmethod
    @abstractmethod
    def HermitianOperatorFromVector(vector):
        """""
        input.vector：GF(2)向量 (2n 长度)
        output：具体子类实例
        """""
        pass

    ##  USER：---检查两个算符是否对易---
    @staticmethod
    @abstractmethod
    def commute(A,B):
        """""
        input.A：算符A
        input.B：算符B
        output：bool，对易返回True
        """""
        pass