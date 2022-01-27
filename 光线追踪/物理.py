import taichi as ti
import enum
from .公共 import *
from .球体 import *
from .矩形 import *
from .传送门 import *
class E与门碰撞(enum.IntEnum):
	e不碰撞 = enum.auto()
	e碰撞 = enum.auto()
	e靠近 = enum.auto()
	e穿过 = enum.auto()
#===============================================================================
# 物体碰撞
#===============================================================================
@ti.func
def sphere_point_no_check(a, b):	#球与固定点的碰撞后处理,不检查是否碰撞
	v位置a = a.m位置[None]
	v速度a = a.m速度[None]
	v方向 = (v位置a - b).normalized()
	v法线 = safe_normal(v方向, v速度a)
	a.m变位置[None] += b + a.m半径 * v方向 - v位置a
	a.m变速度[None] += -v速度a.dot(v方向)*v方向 + v速度a.dot(v法线)*v法线 - v速度a
@ti.func
def sphere_portal(a, b):	#球与一个门之间的碰撞
	v返回 = E与门碰撞.e不碰撞
	v旋转矩阵 = rotation_matrix_y(-b.m旋转[None])
	v旋转矩阵r = rotation_matrix_y(b.m旋转[None])
	v相对位置 = a.m位置[None] - b.m位置[None]
	v相对位置 = v旋转矩阵 @ v相对位置
	v相对位置z = abs(v相对位置.z)
	v相对位置y = abs(v相对位置.y)
	if v相对位置.x > a.m半径:
		pass	#太远
	elif v相对位置z >= c传送门半宽 or v相对位置y >= c传送门半高:
		pass	#在门边框外,不和门碰撞.让球和墙壁碰撞
	elif v相对位置.x < 0:	#在门框内,有穿过门
		v返回 = E与门碰撞.e穿过
	elif v相对位置z > c传送门半宽 - a.m半径:	#可能擦边
		v点 = t向量3(0, v相对位置.y, c传送门半宽*sgn(v相对位置.z))	#离球最近的门边框的点
		if (v相对位置 - v点).norm() < a.m半径:
			v点 = v旋转矩阵r @ v点 + b.m位置[None]
			sphere_point_no_check(a, v点)
			v返回 = E与门碰撞.e碰撞
		else:
			v返回 = E与门碰撞.e靠近
	elif v相对位置y > c传送门半高 - a.m半径:
		v点 = t向量3(0, c传送门半高*sgn(v相对位置.y), v相对位置.z)
		if (v相对位置 - v点).norm() < a.m半径:
			v点 = v旋转矩阵r @ v点 + b.m位置[None]
			sphere_point_no_check(a, v点)
			v返回 = E与门碰撞.e碰撞
		else:
			v返回 = E与门碰撞.e靠近
	else:	#在门框内,没穿过门
		v返回 = E与门碰撞.e靠近
	return v返回
@ti.func
def sphere_portals(a, b):	#球与两个门之间的碰撞
	v结果 = sphere_portal(a, b.m门1)
	if v结果 == E与门碰撞.e不碰撞:
		v结果 = sphere_portal(a, b.m门2)
		if v结果 == E与门碰撞.e碰撞:
			a.m靠近门[None] = 2
		elif v结果 == E与门碰撞.e靠近:
			a.m靠近门[None] = 2
		elif v结果 == E与门碰撞.e穿过:
			a.m位置[None], a.m速度[None] = portal_mirror(b.m门2, b.m门1, a.m位置[None], a.m速度[None])
			a.m靠近门[None] = 1
		else:
			a.m靠近门[None] = 0
	elif v结果 == E与门碰撞.e碰撞:
		a.m靠近门[None] = 1
	elif v结果 == E与门碰撞.e靠近:
		a.m靠近门[None] = 1
	elif v结果 == E与门碰撞.e穿过:
		a.m位置[None], a.m速度[None] = portal_mirror(b.m门1, b.m门2, a.m位置[None], a.m速度[None])
		a.m靠近门[None] = 2
	else:
		a.m靠近门[None] = 0
	pass
@ti.func
def sphere_sphere(a, b):	#球与球之间的碰撞
	v速度a = a.m速度[None]
	v质量a = a.m质量
	v速度b = b.m速度[None]
	v质量b = b.m质量
	v位置差 = b.m位置[None] - a.m位置[None]
	v距离 = v位置差.norm()
	v直径 = a.m半径 + b.m半径
	if v距离 <= v直径:	#发生碰撞
		v拉开距离 = v位置差 * (1 - v距离 / v直径)
		a.m变位置[None] -= v拉开距离
		b.m变位置[None] += v拉开距离
		v质量和 = v质量a + v质量b
		v质量差 = v质量a - v质量b
		v方向 = v位置差 / v距离
		v法线i = safe_normal(v方向, v速度a)
		v法线j = safe_normal(v方向, v速度b)
		v相对速度ix = v速度a.dot(v方向)
		v相对速度iy = v速度a.dot(v法线i)
		v相对速度jx = v速度b.dot(v方向)
		v相对速度jy = v速度b.dot(v法线j)
		v相对速度ix_ = v质量差 / v质量和 * v相对速度ix + 2 * v质量b / v质量和 * v相对速度jx
		v相对速度jx_ = -v质量差 / v质量和 * v相对速度jx + 2 * v质量a / v质量和 * v相对速度ix
		a.m变速度[None] += v相对速度ix_*v方向 + v相对速度iy*v法线i - v速度a
		b.m变速度[None] += v相对速度jx_*v方向 + v相对速度jy*v法线j - v速度b
@ti.func
def mirrorsphere_sphere(a, b):	#镜像球体和普通球体之间的碰撞
	if a.m物体.m靠近门[None] > 0:	#镜像有效性判断
		if b.m靠近门[None] > 0:	#当两个物体同时靠近传送门时,可能在一帧内发生多于一次的碰撞,这时需要去掉重复的碰撞
			if a.m物体.m靠近门[None] == b.m靠近门[None]:	#两个物体在同一侧,不和镜像碰撞
				pass
			elif a.m物体.id < b.id:	#在不同侧,选取id低的一方进行计算
				sphere_sphere(a, b)
		else:
			sphere_sphere(a, b)
@ti.func
def sphere_wall(a, b):	#球与墙之间的碰撞
	if a.m位置[None].x <= -100:	#可能是太极的bug?把这个if去掉或注释掉会出现穿墙情况,哪怕条件恒不成立也不能去掉,也不能改成False
		print(a.m位置[None].x, b.m位置)
	if a.m靠近门[None] > 0:
		pass	#球靠近门时不与墙碰撞
	else:
		#计算球到墙的距离
		v旋转矩阵 = rotation_matrix_y(-b.m旋转)
		v相对位置 = a.m位置[None] - b.m位置
		v相对位置 = v旋转矩阵 @ v相对位置
		if abs(v相对位置.x) >= a.m半径:
			pass	#太远
		elif abs(v相对位置.z) >= b.m半尺寸.x or abs(v相对位置.y) >= b.m半尺寸.y:
			pass	#太远
			#偷懒,没有做更详细的判断
		else:	#碰撞
			v相对位置.x = a.m半径
			v相对速度 = v旋转矩阵 @ a.m速度[None]
			v相对速度.x = -v相对速度.x	#无速度损失
			v旋转矩阵r = rotation_matrix_y(b.m旋转)
			a.m变位置[None] += v旋转矩阵r @ v相对位置 + b.m位置 - a.m位置[None]
			a.m变速度[None] += v旋转矩阵r @ v相对速度 - a.m速度[None]
@ti.func
def sphere_floor(a, b):	#球与地板之间的碰撞
	v相对位置 = a.m位置[None] - b.m位置
	v碰撞 = False
	if abs(v相对位置.x) >= b.m半尺寸.x or abs(v相对位置.z) >= b.m半尺寸.y:	#在矩形外
		pass
	elif b.m天花板:	#天花板
		if v相对位置.y > -a.m半径:
			v相对位置.y = -a.m半径
			v碰撞 = True
	else:	#地板
		if v相对位置.y < a.m半径:
			v相对位置.y = a.m半径
			v碰撞 = True
	if v碰撞:
		a.m变位置[None] += v相对位置 + b.m位置 - a.m位置[None]
		a.m变速度[None].y -= a.m速度[None].y * 1.99	#有速度损失
#===============================================================================
# 碰撞类
#===============================================================================
@ti.data_oriented
class C物体碰撞:
	def __init__(self, a物体1, a物体2, a函数):
		self.m物体1 = a物体1
		self.m物体2 = a物体2
		self.m函数 = a函数
	@staticmethod
	def f自动(a物体1, a物体2):	#返回:优先级,物体碰撞
		v类型1 = type(a物体1)
		v类型2 = type(a物体2)
		if v类型1 == C球体:
			if v类型2 == C球体:
				return 1, C物体碰撞(a物体1, a物体2, sphere_sphere)
			elif v类型2 == C墙壁:
				return 1, C物体碰撞(a物体1, a物体2, sphere_wall)
			elif v类型2 == C地板:
				return 1, C物体碰撞(a物体1, a物体2, sphere_floor)
			elif v类型2 == C传送门组:
				return 0, C物体碰撞(a物体1, a物体2, sphere_portals)
		elif v类型1 == C墙壁:
			if v类型2 == C球体:
				return 1, C物体碰撞(a物体2, a物体1, sphere_wall)
		elif v类型1 == C地板:
			if v类型2 == C球体:
				return 1, C物体碰撞(a物体2, a物体1, sphere_floor)
		elif v类型1 == C传送门组:
			if v类型2 == C球体:
				return 0, C物体碰撞(a物体2, a物体1, sphere_portals)
		elif v类型1 == C镜像球体:
			if v类型2 == C球体:
				return 1, C物体碰撞(a物体1, a物体2, mirrorsphere_sphere)
		#没有镜像和镜像之间的碰撞,因为如果两个镜像发生碰撞,则对应的原始物体也必然发生碰撞
		return 0, None
	@ti.func
	def compute(self):
		self.m函数(self.m物体1, self.m物体2)
#===============================================================================
# 物理引擎
#===============================================================================
c重力加速度 = 1
@ti.data_oriented
class C物理参数:
	def __init__(self, a重力加速度 = c重力加速度):
		self.m重力加速度 = a重力加速度
@ti.data_oriented
class C物理:
	def __init__(self, a场景, a物理参数):
		self.m物理参数 = a物理参数
		self.m物体 = []
		self.m镜像 = a场景.m镜像
		self.m碰撞列表 = [[], []]	#开始计算之前,先整成一个碰撞列表,计算时直接遍历这个列表就行
		self.m传送门组 = None
		if not a场景:	#可以为空
			return
		for i in range(len(a场景.m物体)):
			#是否有计算
			v物体i = a场景.m物体[i]
			if hasattr(v物体i, "compute"):
				self.m物体.append(v物体i)
			if type(v物体i) == C传送门组:
				self.m传送门组 = v物体i	#单独拎出来
			#物体交互
			if v物体i.m碰撞:
				for j in range(i):
					#根据类型得到相应的碰撞函数
					v物体j = a场景.m物体[j]
					if v物体j.m碰撞:
						v优先级, v物体碰撞 = C物体碰撞.f自动(v物体i, v物体j)
						if v物体碰撞:
							self.m碰撞列表[v优先级].append(v物体碰撞)
		for i in range(len(a场景.m镜像)):
			v镜像i = a场景.m镜像[i]
			for v物体j in self.m物体:
				if v镜像i.m物体 == v物体j:
					continue	#同一个物体
				v优先级, v物体碰撞 = C物体碰撞.f自动(v镜像i, v物体j)
				if v物体碰撞:
					self.m碰撞列表[v优先级].append(v物体碰撞)
	@ti.kernel
	def compute(self, dt: float):
		for i in ti.static(range(len(self.m镜像))):	#镜像计算,把变化转移给原始物体
			self.m镜像[i].compute(self.m传送门组)
		for i in ti.static(range(len(self.m物体))):	#物体计算
			self.m物体[i].compute(self.m物理参数, dt)
		for i in ti.static(range(len(self.m碰撞列表[0]))):	#与传送门碰撞
			self.m碰撞列表[0][i].compute()
		for i in ti.static(range(len(self.m镜像))):	#与传送门碰撞后更新镜像状态
			self.m镜像[i].mirror(self.m传送门组)
		for i in ti.static(range(len(self.m碰撞列表[1]))):	#普通物体碰撞
			self.m碰撞列表[1][i].compute()
