"""""
模块作用：提供GF(2)线性代数与组合优化相关的工具方法，如解线性方程、子空间交并、正交化、码距估计等。
"""""
import galois
import numpy as np
from mip import Model, BINARY, minimize, xsum


##  USER：---解GF(2)线性方程组 A^T x = b---
def solve(matrix, vector):
    """""
    input.matrix：galois.GF(2) 或 01矩阵，形状 (m, n)
    input.vector：galois.GF(2) 或 01向量，形状 (n,)
    output：galois.GF(2) 向量解；若无解返回 None
    """""

    ##  ---数据预处理---
    assert matrix.shape[1] == vector.shape[0]
    A = matrix.T
    b = vector.reshape(-1, 1)

    ##  ---求解线性方程---
    aug = np.concatenate((A, b), axis=1)
    n, m_plus_1 = aug.shape
    m = m_plus_1 - 1
    rank = 0
    for col in range(m):
        ##  寻找主元
        pivot_row = None
        for i in range(rank, n):
            if aug[i, col] == 1:
                pivot_row = i
                break
        if pivot_row is None:
            ##  该列没有主元，跳过
            continue
        ##  交换行
        if pivot_row != rank:
            aug[[rank, pivot_row], :] = aug[[pivot_row, rank], :]
        ##  消去当前列下方和上方的元素
        for i in range(n):
            if i != rank and aug[i, col] == 1:
                aug[i, :] ^= aug[rank, :]
        rank += 1

    ##  检查是否有解
    for i in range(rank, n):
        if aug[i, -1] == 1:
            return None  # 无解的情况

    ##  构造解向量
    GF=galois.GF(2)
    solution = GF.Zeros(m)
    leading_cols = []

    ##  找出主元列
    for i in range(rank):
        for j in range(m):
            if aug[i, j] == 1:
                leading_cols.append(j)
                break

    ##  回代求解
    for i in range(rank):
        col = leading_cols[i]
        solution[col] = aug[i, -1]

        ##  消去当前行中主元列右侧的元素对解的影响
        for j in range(col + 1, m):
            if aug[i, j] == 1:
                solution[col] ^= solution[j]

    ##  ---返回解向量---
    return solution


##  USER：---返回两个线性空间的交集---
def cap(matrix1, matrix2):
    """""
    input.matrix1：GF(2)矩阵，行张成子空间1
    input.matrix2：GF(2)矩阵，行张成子空间2
    output：GF(2)矩阵，表示交集的行空间基
    """""

    ##  ---数据预处理---
    m = matrix1.shape[0]
    k = matrix2.shape[0]

    ##  解方程 basis1^T * x + basis2^T * y = 0 (表示交集向量), 构造矩阵 [basis1^T | basis2^T]
    aug_matrix = galois.GF(2)(np.concatenate((matrix1.T, matrix2.T), axis=1))

    ##  计算零空间（解空间）
    nullspace = aug_matrix.null_space()

    ##  从零空间中取对应于每个解向量的系数（对应于方程组中的解向量）
    ab_space = nullspace[:, :m]

    ##  将系数乘以 basis1 得到具体解（交集）
    if len(ab_space) == 0:
        return galois.GF(2).Zeros((0, matrix1.shape[1]))

    intersection_vectors = ab_space @ matrix1

    ##  产生基向量的线性无关组合，即每种向量的不同的高斯行组合样本
    rref_intersection = intersection_vectors.row_reduce()

    ##  除去全0行的行（即为没有有用基底捕获的时候）
    nz_mask = np.any(rref_intersection != 0, axis=1)
    rref_basis = rref_intersection[nz_mask]

    ##  返回补集
    return rref_basis


##  USER：---返回两个线性空间的差集（matrix1 \ cap(matrix1,matrix2)）---
def minus(matrix1, matrix2):
    """""
    input.matrix1：GF(2)矩阵，行张成子空间1
    input.matrix2：GF(2)矩阵，行张成子空间2
    output：列表[ndarray]，为子空间差的基向量（01行向量）
    """""

    ##  ---数据预处理---
    assert matrix1.shape[1] == matrix2.shape[1]

    ##  转化为GF2数组
    matrix1_origin = matrix1
    matrix2_origin = matrix2
    matrix1 = matrix1._array
    matrix2 = matrix2._array

    intersect = cap(matrix1_origin, matrix2_origin)._array
    if len(intersect) == 0:
        return galois.GF(2)(matrix1)

    result = []
    for i in range(len(matrix1)):
        rank = np.linalg.matrix_rank(intersect)
        intersect = np.vstack((intersect, matrix1[i]))
        if np.linalg.matrix_rank(intersect) > rank:
            result.append(matrix1[i])

    ##  返回差集
    return result


##  USER：---返回两个线性空间的直和基（合并并去冗余）---
def direct_sum(matrix1, matrix2):
    """""
    input.matrix1：GF(2)矩阵
    input.matrix2：GF(2)矩阵
    output：GF(2)矩阵，直和后的独立基
    """""
    assert isinstance(matrix1, galois.GF(2))
    assert isinstance(matrix2, galois.GF(2))

    ##  转化为GF2数组
    result = matrix1[0].copy()

    ##  直接拼接
    for i in range(1, len(matrix1)):
        rank = np.linalg.matrix_rank(result)
        temp = np.vstack((result, matrix1[i]))
        if np.linalg.matrix_rank(temp) > rank:
            result = temp
    for i in range(len(matrix2)):
        rank = np.linalg.matrix_rank(result)
        temp = np.vstack((result, matrix2[i]))
        if np.linalg.matrix_rank(temp) > rank:
            result = temp

    ##  返回结果
    return galois.GF(2)(result)


##  USER：---正交化基矢组（相对于标准内积）---
def orthogonalize(matrix):
    """""
    input.matrix：可迭代的GF(2)行向量列表/矩阵
    output：列表[GF(2)行向量]，两两正交的基
    """""

    ##  双线性形式矩阵
    B_i=[v.copy() for v in matrix]
    ortho_basis=[]  # 存储正交基

    while True:

        ##  遍历B_i，找到奇数权重向量
        length=len(B_i)
        for i in range(length):
            if np.mod(np.count_nonzero(B_i[i]), 2)==1:
                for j in range(length):
                    if j!=i and np.mod(np.count_nonzero(B_i[j]), 2)==0:
                        B_i[j]=B_i[j]+B_i[i]
                break
        flag=0
        b1=B_i[0]
        o_i=b1
        ortho_basis.append(o_i)
        next_B=[]
        for j in range(len(B_i)):
            if j!=flag:
                b=B_i[j]
                coef=np.dot(b, o_i)
                b_new=b+coef*o_i
                next_B.append(b_new)
        B_i=next_B
        if len(B_i)==0:
            break

    ##  ---返回正交基---
    return ortho_basis


##  USER：---计算code distance---
def distance(H, method:str,search_number:int=500)->int:
    """""
    input.H：GF(2)矩阵，稳定子或校验矩阵
    input.method：'mip' 或 'random'
    input.search_number：随机法搜索次数
    output：int，最小码距估计
    """""
    if method == 'mip':
        logic_op = minus(H.null_space(), H)
        return mip_distance_caculator(H, logic_op)
    elif method == 'random':
        return random_distance_caculator(H, H, search_number)
    else:
        raise NotImplementedError


#%%  KEY：===计算code distance===
def mip_distance_caculator(H, logicOp)->int:
    """""
    input.H：01矩阵或GF(2)矩阵
    input.logicOp：01矩阵或GF(2)矩阵，逻辑算子候选
    output：int，最小权重
    """""

    ##  格式化输入
    H = np.array(H, dtype=int)  # 转换为整数类型的numpy数组
    logicOp = np.array(logicOp, dtype=int)  # 转换为整数类型的numpy数组
    d = H.shape[1]  # 初始化距离为量子比特数量（最大可能距离）

    ##  遍历每个逻辑算子
    for i in range(logicOp.shape[0]):
        logicOp_i = logicOp[i, :]
        n = H.shape[1]  # 量子比特数量（稳定子矩阵的列数）
        m = H.shape[0]  # 稳定子数量（稳定子矩阵的行数）
        wstab = np.max([np.sum(H[i, :]) for i in range(m)])  # 计算最大稳定子权重（单个稳定子中非零元素的最大数量）
        wlog = np.count_nonzero(logicOp_i)  # 计算逻辑算子的权重
        num_anc_stab = int(np.ceil(np.log2(wstab)))  # 计算稳定子约束所需的辅助变量数量（基于最大稳定子权重的对数）
        num_anc_logical = int(np.ceil(np.log2(wlog)))  # 计算逻辑算子约束所需的辅助变量数量（基于逻辑算子权重的对数）
        num_var = n + m * num_anc_stab + num_anc_logical  # 总变量数量 = 量子比特变量 + 稳定子辅助变量 + 逻辑算子辅助变量

        ##  创建混合整数规划模型
        model = Model()
        model.verbose = 0  # 关闭详细输出
        x = [model.add_var(var_type=BINARY) for i in range(num_var)]  # 创建二进制变量数组
        model.objective = minimize(xsum(x[i] for i in range(n)))  # 目标函数：最小化前n个变量（量子比特变量）的和（即最小化Hamming权重）

        # 为每个稳定子添加正交性约束（模2）
        for row in range(m):
            weight = [0] * num_var  # 初始化权重向量
            supp = np.nonzero(H[row, :])[0]  # 获取当前稳定子的支持集（非零元素的位置）

            ##  设置qubit变量的权重为1
            for q in supp:
                weight[q] = 1

            ##  添加辅助变量来处理模2约束
            cnt = 1
            for q in range(num_anc_stab):
                weight[n + row * num_anc_stab + q] = -(1 << cnt)  # 设置辅助变量的权重为负的2的幂次方
                cnt += 1
            model += xsum(weight[i] * x[i] for i in range(num_var)) == 0  # 添加约束：权重向量与变量向量的点积等于0

        ##  添加逻辑算子的奇数重叠约束
        supp = np.nonzero(logicOp_i)[0]  # 获取逻辑算子的支持集
        weight = [0] * num_var  # 初始化权重向量

        ##  设置qubit变量的权重为1
        for q in supp:
            weight[q] = 1

        ##  添加辅助变量来处理模2约束
        cnt = 1
        for q in range(num_anc_logical):
            # 设置辅助变量的权重为负的2的幂次方
            weight[n + m * num_anc_stab + q] = -(1 << cnt)
            cnt += 1

        ##  添加约束：权重向量与变量向量的点积等于1（奇数重叠）
        model += xsum(weight[i] * x[i] for i in range(num_var)) == 1

        ##  求解优化问题，计算最优解中前n个变量的和，即最小Hamming权重
        model.optimize()
        # noinspection PyTypeChecker
        opt_val = sum([x[i].x for i in range(n)])
        d = min(d, int(opt_val))

    ##  返回最小距离
    return d


#%%  KEY：===计算随机距离===
def random_distance_caculator(gx, gz, num)->int:
    """""
    input.gx：GF(2)矩阵
    input.gz：GF(2)矩阵
    input.num：搜索迭代次数
    output：int，随机启发式最小权重
    """""

    ##  设置默认有限域为GF(2)（二进制域）
    F = galois.GF(2)

    wz = F(gx.null_space())  # 计算X稳定子的零空间（Z逻辑算子空间）
    wx = F(gz.null_space())  # 计算Z稳定子的零空间（X逻辑算子空间）
    rows_wz, cols_wz = wz.shape  # 获取零空间矩阵的维度信息
    dist_bound = cols_wz + 1  # 初始化距离上界为最大可能值（列数+1）
    vec_count = 0  # 计数器：记录找到当前最小权重的向量数量

    ##  主循环：进行num次随机迭代
    for i in range(num):
        per = np.random.permutation(cols_wz)  # 生成随机排列，用于随机化搜索顺序
        wz1 = wz[:, per]  # 对零空间矩阵的列进行随机排列
        wz2 = wz1.row_reduce()  # 对排列后的矩阵进行行约简（高斯消元）
        wz2 = wz2[:, np.argsort(per)]  # 将列顺序恢复为原始顺序

        ##  遍历行约简后的每一行
        for j in range(rows_wz):
            temp_vec = wz2[j, :]  # 获取当前行向量
            temp_weight = np.count_nonzero(temp_vec)  # 计算向量的Hamming权重（非零元素个数）

            ##  检查权重是否在有效范围内且小于等于当前最小距离
            if 0 < temp_weight <= dist_bound:

                ##  检查向量是否与X逻辑算子空间有非零重叠（即是否为非平凡逻辑算子）
                if np.any(wx @ temp_vec):

                    ##  如果找到更小的权重，更新最小距离
                    if temp_weight < dist_bound:
                        dist_bound = temp_weight
                        vec_count = 1

                    ##  如果权重等于当前最小距离，增加计数器
                    elif temp_weight == dist_bound:
                        vec_count += 1

            ##  检查是否达到最小距离阈值，如果达到则提前终止
            if dist_bound <= 2:
                return 2

    ##  返回找到的最小距离
    return dist_bound


##  USER：---生成循环移位矩阵---
def shift(number:'int', shift:'int'):
    """""
    input.number：矩阵维度
    input.shift：循环移位步长
    output：GF(2)矩阵，置换矩阵
    """""

    S = np.zeros((number, number), dtype=int)
    for i in range(number):
        S[i, (i + shift) % number] = 1
    return galois.GF(2)(S)


##  USER：---返回向量中为1的下标---
def occupy(vector):
    """""
    input.vector：01向量或GF(2)向量
    output：ndarray，值为1的位置索引
    influence：从向量表示提取支撑集
    """""

    return np.where(vector==1)[0]
