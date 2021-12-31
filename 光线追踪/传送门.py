import taichi as ti
from .公共 import *
c传送门宽度 = 1
c传送门高度 = 2
c传送门半宽 = c传送门宽度 * 0.5
c传送门半高 = c传送门高度 * 0.5
@ti.func
def ellipse_equation(x, y):	#椭圆方程x^2/a^2 + y^2/b^2 = 1
	return x**2/c传送门半宽**2 + y**2/c传送门半高**2
@ti.data_oriented
class C传送门:
	def __init__(self, a位置: t向量3, a旋转: float, a颜色: t向量3):
		self.m位置 = new_field(t向量3, a位置)	#位置
		self.m旋转 = new_field(float, a旋转)	#角度
		self.m颜色 = new_field(t向量3, a颜色)	#传送门边缘的颜色
	@ti.func
	def ray_hit0(self, a光线, a最小值, a最大值):
		#返回t
		v旋转矩阵 = rotation_matrix_y(-self.m旋转[None])
		v相对位置 = a光线.m位置 - self.m位置[None]
		v相对位置 = v旋转矩阵 @ v相对位置
		v相对方向 = v旋转矩阵 @ a光线.m方向
		t = 0.0
		v碰撞 = False
		r = 0.0
		if v相对位置.x < 0:
			pass
		elif v相对方向.x >= 0:
			pass
		else:
			t = -v相对位置.x / v相对方向.x
			v相对交点 = v相对位置 + v相对方向 * t
			if t <= a最小值 or t >= a最大值:
				pass
			r = ellipse_equation(v相对交点.z, v相对交点.y)
			if r <= 1:	#在椭圆内
				v碰撞 = True
			else:
				pass
		return v碰撞, t, r
	#属性
	@ti.func
	def nomarlized(self):
		return t向量3(ti.cos(-self.m旋转[None]), 0.0, ti.sin(-self.m旋转[None]))
#===============================================================================
# 两个门一组
#===============================================================================
@ti.data_oriented
class C传送门组:
	def __init__(self, a门1, a门2):
		self.m门1 = a门1
		self.m门2 = a门2
		self.m碰撞 = True
	@ti.func
	def ray_hit(self, a光线, a最小值, a最大值):
		v交点 = t向量3(0, 0, 0)
		v方向 = t向量3(0, 0, 0)
		v颜色 = t向量3(1, 1, 1)	#入门的颜色
		v碰撞 = False
		t = 0.0
		v碰撞, t, r = self.m门1.ray_hit0(a光线, a最小值, a最大值)
		if v碰撞:	#光线和门1碰撞,返回光线从门2出来的位置方向
			v交点, v方向 = portal_mirror(self.m门1, self.m门2, a光线.at(t), a光线.m方向)
			v颜色 = self.m门1.m颜色[None]
		else:
			v碰撞, t, r = self.m门2.ray_hit0(a光线, a最小值, a最大值)
			if v碰撞:
				v交点, v方向 = portal_mirror(self.m门2, self.m门1, a光线.at(t), a光线.m方向)
				v颜色 = self.m门2.m颜色[None]
		#根据交点到椭圆边缘的半径r,计算光线颜色
		if r <= 2.0 / 3.0:
			v颜色 = t向量3(1, 1, 1)	#在靠内的位置,不改变光线颜色
		elif r >= 1:
			pass	#门外,使用门的颜色
		else:
			v颜色 = lerp(t向量3(1, 1, 1), v颜色, (r - 2.0 / 3.0) * 3.0)	#靠近边缘,使用门的颜色
		#返回
		return v碰撞, t, v交点, v方向, True, v颜色, E材质.e传送门
#===============================================================================
# 计算镜像
#===============================================================================
@ti.func
def portal_mirror(a前, a后, a位置, a方向):	#计算物体位置方向相对于另一个传送门的位置方向
	v镜像 = C传送门镜像(a前, a后)
	v位置 = v镜像.mirror_position(a位置)
	v方向 = v镜像.mirror_direction(a方向)
	return v位置, v方向
@ti.data_oriented
class C传送门镜像:	#用来计算物体穿过传送门时的相对位置的相对方向的类
	def __init__(self, a门1, a门2):
		self.m门1 = a门1
		self.m门2 = a门2
		#在 __init__ 写 rotation_matrix_y(-self.m门1.m旋转[None]) 会报错,先用随便矩阵占坑再初始化
		self.m旋转矩阵1 = ti.Matrix([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
		self.m旋转矩阵2 = ti.Matrix([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
		self.init()
	@ti.func
	def init(self):
		self.m旋转矩阵1 = rotation_matrix_y(-self.m门1.m旋转[None])	#提前计算好矩阵,方便循环使用
		self.m旋转矩阵2 = rotation_matrix_y(self.m门2.m旋转[None])
	@ti.func
	def mirror_position(self, a位置):
		v位置 = a位置
		v位置 -= self.m门1.m位置[None]
		v位置 = self.m旋转矩阵1 @ v位置
		v位置.x = -v位置.x
		v位置.z = -v位置.z
		v位置 = self.m旋转矩阵2 @ v位置
		v位置 += self.m门2.m位置[None]
		return v位置
	@ti.func
	def mirror_direction(self, a方向):
		v方向 = a方向
		v方向 = self.m旋转矩阵1 @ v方向
		v方向.x = -v方向.x
		v方向.z = -v方向.z
		v方向 = self.m旋转矩阵2 @ v方向
		return v方向