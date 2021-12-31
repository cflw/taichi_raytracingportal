import taichi as ti
from .公共 import *
#===============================================================================
# 相机
#===============================================================================
@ti.data_oriented
class C相机:	#生成光线
	def __init__(self, a位置: t向量3, a目标: t向量3, a上方: t向量3):
		self.m位置 = a位置
		self.m目标 = a目标
		self.m上方 = a上方
#===============================================================================
# 透视投影
#===============================================================================
@ti.data_oriented
class C透视投影:
	def __init__(self, a宽高比: float = 1, a视角: float = PI / 3):
		self.m宽高比 = a宽高比
		self.m视角 = a视角
@ti.data_oriented
class C透视投射:
	def __init__(self, a相机: C相机, a透视: C透视投影):
		self.m位置 = a相机.m位置
		v半高 = ti.tan(a透视.m视角 / 2)
		v半宽 = v半高 * a透视.m宽高比
		w = (a相机.m位置 - a相机.m目标).normalized()
		u = a相机.m上方.cross(w).normalized()
		v = w.cross(u)
		self.m左下角 = a相机.m位置 - v半宽 * u - v半高 * v - w
		self.m水平 = 2 * v半宽 * u
		self.m垂直 = 2 * v半高 * v
	@ti.func
	def get_ray(self, u: float, v: float):
		return C光线(self.m位置, self.m左下角 + u * self.m水平 + v * self.m垂直 - self.m位置)
#===============================================================================
# 正交投影
#===============================================================================
@ti.data_oriented
class C正交投影:
	def __init__(self, a宽: float, a高: float):
		self.m宽 = a宽
		self.m高 = a高
@ti.data_oriented
class C正交投射:
	def __init__(self, a相机: C相机, a正交: C正交投影):
		self.m方向 = (a相机.m目标 - a相机.m位置).normalized()
		v半宽 = a正交.m宽 * 0.5
		v半高 = a正交.m高 * 0.5
		u = -a相机.m上方.cross(self.m方向).normalized()
		v = -self.m方向.cross(u)
		self.m左下角 = a相机.m位置 - v半宽 * u - v半高 * v
		self.m水平 = 2 * v半宽 * u
		self.m垂直 = 2 * v半高 * v
	@ti.func
	def get_ray(self, u: float, v: float):
		return C光线(self.m左下角 + u * self.m水平 + v * self.m垂直, self.m方向)
#===============================================================================
# 函数
#===============================================================================
def f创建光线投射器(a相机, a投影):
	if isinstance(a投影, C透视投影):
		return C透视投射(a相机, a投影)
	elif isinstance(a投影, C正交投影):
		return C正交投射(a相机, a投影)
	raise ValueError()