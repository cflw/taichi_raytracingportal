import taichi as ti
from .公共 import *
from .传送门 import *
c球体密度 = 1
@ti.func
def ray_hit_sphere(a光线, a最小值, a最大值, a位置, a半径, a颜色, a材质):
	v相对位置 = a光线.m位置 - a位置
	a = a光线.m方向.dot(a光线.m方向)
	b = 2 * v相对位置.dot(a光线.m方向)
	c = v相对位置.dot(v相对位置) - a半径*a半径
	d = b * b - 4 * a * c
	x = 0.0
	if d > 0.0:
		sqrt_d = ti.sqrt(d)
		x = (-b - sqrt_d) / (2 * a)
		if x <= a最小值 or x >= a最大值:
			x = (-b + sqrt_d) / (2 * a)
			if x <= a最小值 or x >= a最大值:
				x = 0.0
	else:
		x = 0.0
	#返回
	v碰撞 = False
	v交点 = t向量3(0, 0, 0)
	v交点法线 = t向量3(0, 0, 0)
	v前面 = False
	if x > 0.0:
		v碰撞 = True
		v交点 = a光线.at(x)
		v交点法线 = (v交点 - a位置).normalized()
		if a光线.m方向.dot(v交点法线) < 0:
			v前面 = True
		else:
			v交点法线 = -v交点法线
	return v碰撞, x, v交点, v交点法线, v前面, a颜色, a材质
@ti.data_oriented
class C球体:
	def __init__(self, a位置: t向量3, a半径: float, a颜色: t向量3, a材质, a速度: t向量3 = None, a碰撞 = True):
		self.m位置 = new_field(t向量3, a位置)
		self.m速度 = new_field(t向量3, a速度)
		self.m变位置 = new_field(t向量3)
		self.m变速度 = new_field(t向量3)
		self.m靠近门 = new_field(int, 0)	#数字几表示靠近哪个门,0表示没有靠近任何门,在球与门计算中更新值
		self.m质量 = 4 /3 * PI * a半径**3 * c球体密度
		self.m半径 = a半径
		self.m颜色 = a颜色	#物体反射光
		self.m材质 = a材质
		self.m碰撞 = a碰撞	#参与物体碰撞
		self.id = id(self)	#比较碰撞优先级时使用
	def mirror_object(self):
		return C镜像球体(self)
	@ti.func
	def ray_hit(self, a光线, a最小值, a最大值):	#求光线交于圆表面的距离,不相交则返回0
		return ray_hit_sphere(a光线, a最小值, a最大值, self.m位置[None], self.m半径, self.m颜色, self.m材质)
	@ti.func
	def compute(self, a物理参数, dt):	#计算
		self.m速度[None] += self.m变速度[None]
		self.m速度[None].y -= a物理参数.m重力加速度 * dt
		self.m位置[None] += self.m变位置[None] + self.m速度[None] * dt
		self.m变位置[None] = t向量3(0, 0, 0)
		self.m变速度[None] = t向量3(0, 0, 0)
@ti.data_oriented
class C镜像球体:
	def __init__(self, a球体):
		self.m物体 = a球体
		self.m位置 = new_field(t向量3)
		self.m速度 = new_field(t向量3)
		self.m变位置 = new_field(t向量3)
		self.m变速度 = new_field(t向量3)
		self.m半径 = a球体.m半径
		self.m质量 = a球体.m质量
	@ti.func
	def ray_hit(self, a光线, a最小值, a最大值):
		return ray_hit_sphere(a光线, a最小值, a最大值, self.m位置[None], self.m半径, self.m物体.m颜色, self.m物体.m材质)
	@ti.func
	def mirror0(self, a门1, a门2):
		self.m位置[None], self.m速度[None] = portal_mirror(a门1, a门2, self.m物体.m位置[None], self.m物体.m速度[None])
	@ti.func
	def mirror(self, a传送门组):	#计算镜像球体自身的位置
		v靠近门 = self.m物体.m靠近门[None]
		if v靠近门 == 0:
			pass
		elif v靠近门 == 1:
			self.mirror0(a传送门组.m门1, a传送门组.m门2)
		elif v靠近门 == 2:
			self.mirror0(a传送门组.m门2, a传送门组.m门1)
	@ti.func
	def compute0(self, a门1, a门2):
		v镜像 = C传送门镜像(a门1, a门2)
		v变速度 = v镜像.mirror_direction(self.m变速度[None])
		self.m物体.m速度[None] += v变速度
		v变位置 = v镜像.mirror_direction(self.m变位置[None])
		self.m物体.m位置[None] += v变位置
	@ti.func
	def compute(self, a传送门组):
		v靠近门 = self.m物体.m靠近门[None]
		if v靠近门 == 0:
			pass
		elif v靠近门 == 1:	#当物体靠近门1时,镜像靠近的是门2
			self.compute0(a传送门组.m门2, a传送门组.m门1)
		elif v靠近门 == 2:
			self.compute0(a传送门组.m门1, a传送门组.m门2)
		self.m变速度[None] = t向量3(0, 0, 0)
		self.m变位置[None] = t向量3(0, 0, 0)