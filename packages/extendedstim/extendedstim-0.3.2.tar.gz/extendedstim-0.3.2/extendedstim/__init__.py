#%%  USER：===模块导入与别名===
"""
模块作用：集中导入ExtendedStim内部的主要类并提供简化别名，方便用户直接使用。
output.PauliCode 等：分别为各量子编码与电路相关类的别名。
influence：导入时执行底层模块初始化（若有）。不执行任何额外逻辑。
"""
import extendedstim.Code.QuantumCode.QuantumCode
import extendedstim.Code.QuantumCode.QuantumCSSCode
import extendedstim.Code.QuantumCode.PauliCode
import extendedstim.Code.QuantumCode.PauliCSSCode
import extendedstim.Code.QuantumCode.MajoranaCode
import extendedstim.Code.QuantumCode.MajoranaCSSCode
import extendedstim.Code.LinearCode.LinearCode
import extendedstim.Code.LinearCode.BicycleCode
import extendedstim.Code.LinearCode.FiniteEuclideanGeometryCode
import extendedstim.Code.LinearCode.FiniteProjectiveGeometryCode
import extendedstim.Circuit.Circuit
import extendedstim.Circuit.Code2Circuit
import extendedstim.Circuit.Code2Circuit

#%%  USER：===别名导出===
"""
将常用类统一导出为顶层别名，方便用户直接 `from extendedstim import PauliCode` 等调用。
"""
PauliCode=extendedstim.Code.QuantumCode.PauliCode.PauliCode
PauliCSSCode=extendedstim.Code.QuantumCode.PauliCSSCode.PauliCSSCode
MajoranaCode=extendedstim.Code.QuantumCode.MajoranaCode.MajoranaCode
MajoranaCSSCode=extendedstim.Code.QuantumCode.MajoranaCSSCode.MajoranaCSSCode
LinearCode=extendedstim.Code.LinearCode.LinearCode.LinearCode
BicycleCode=extendedstim.Code.LinearCode.BicycleCode.BicycleCode
FiniteEuclideanGeometryCode=extendedstim.Code.LinearCode.FiniteEuclideanGeometryCode.FiniteEuclideanGeometryCode
FiniteProjectiveGeometryCode=extendedstim.Code.LinearCode.FiniteProjectiveGeometryCode.FiniteProjectiveGeometryCode
Code2Circuit=extendedstim.Circuit.Code2Circuit.Code2Circuit
Circuit=extendedstim.Circuit.Circuit.Circuit
