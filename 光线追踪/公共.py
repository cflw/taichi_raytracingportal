import taichi as ti
import enum
#标量常量
PI = 3.14159265
半PI = 1.5707963
二PI = 6.2831853
c最小值 = 0.001
c最大值 = 10e4
#输出
c窗口尺寸 = (480, 480)
c视频尺寸 = (1920, 1920)
c宽高比 = c窗口尺寸[0] / c窗口尺寸[1]
c窗口尺寸w = (480, 270)
c视频尺寸w = (1920, 1080)
c宽高比w = c窗口尺寸w[0] / c窗口尺寸w[1]
c帧速率 = 60
c时间差 = 1 / c帧速率
c时间细分 = 10
#类型
t向量2 = ti.types.vector(2, float)
t向量3 = ti.types.vector(3, float)
t向量4 = ti.types.vector(4, float)
#向量常量
c白 = t向量3(1.0, 1.0, 1.0)
c黑 = t向量3(0.0, 0.0, 0.0)
c传送门蓝 = t向量3(0.3, 0.3, 1.0)
c传送门橙 = t向量3(1.0, 0.5, 0.1)
c背景色 = t向量3(0.0, 0.0, 0.0)
c发光颜色 = t向量3(0, 0, 0)	#不发光
c反射颜色 = t向量3(1, 1, 1)	#全反射
#枚举
class E材质(enum.IntEnum):
	e光源 = enum.auto()
	e漫反射 = enum.auto()
	e镜面反射 = enum.auto()
	e折射 = enum.auto()
	e模糊反射 = enum.auto()	#带点模糊的镜面反射
	e传送门 = enum.auto()
	e叠加 = enum.auto()
#===============================================================================
# 函数
#===============================================================================
def f新建场(a类型, a初始值 = None):	#新建一个零维场,并赋值
	if a类型 in (int, float):	#标量
		v场 = ti.field(a类型, shape = ())
	elif a类型 == bool:
		v场 = ti.field(ti.int32, shape = ())
	else:
		v场 = a类型.field(shape = ())
	if a初始值 != None:
		v场[None] = a初始值
	return v场
@ti.func
def sgn(a):	#符号函数
	return 1 if a >= 0 else -1
@ti.func
def lerp(a, b, t):	#插值
	return a + (b - a) * t
@ti.func
def f旋转矩阵y(rad: float):
	c = ti.cos(rad)
	s = ti.sin(rad)
	return ti.Matrix([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
@ti.func
def f随机向量3():	#随机向量3
	return t向量3(ti.random(), ti.random(), ti.random())
@ti.func
def f随机单位球体():	#单位球体内随机取值
	θ = 2.0 * PI * ti.random()
	φ = ti.acos((2.0 * ti.random()) - 1.0)
	r = ti.pow(ti.random(), 1.0/3.0)
	return t向量3(r * ti.sin(φ) * ti.cos(θ), r * ti.sin(φ) * ti.sin(θ), r * ti.cos(φ))
@ti.func
def f随机单位向量():
	return f随机单位球体().normalized()
@ti.func
def f反射(v, n):	#反射
	return v - 2 * v.dot(n) * n
@ti.func
def f折射(uv, n, etai_over_etat):	#折射
	cosθ = min(n.dot(-uv), 1.0)
	r_out_perp = etai_over_etat * (uv + cosθ * n)
	r_out_parallel = -ti.sqrt(abs(1.0 - r_out_perp.dot(r_out_perp))) * n
	return r_out_perp + r_out_parallel
@ti.func
def f反射比(cosine, ref_idx):	#反射比
	# 施力克近似（Schlick's approximation）求反射透明度
	r0 = (1 - ref_idx) / (1 + ref_idx)
	r0 = r0 * r0
	return r0 + (1 - r0) * pow((1 - cosine), 5)
@ti.func
def f法线(a方向, a速度):	#安全地计算法线,最多返回0,不会有nan
	v法线 = t向量3(0, 0, 0)
	if a方向.norm() != 0 and a速度.norm() != 0:
		v法线 = a方向.cross(a速度).cross(a方向)
		v范数 = v法线.norm()
		if v范数 != 0:
			v法线 /= v范数
	return v法线
@ti.func
def f异面直线距离(p1, d1, p2, d2):
	n = d1.cross(d2)
	return ti.abs(n.dot(p2 - p1)) / n.norm()
@ti.func
def f异面直线最近位置(p1, d1, p2, d2):	#位置和方向
	d3 = d1.cross(d2)	#d1,d2的垂直方向
	n = d2.cross(d3)	#平面法线
	a, b, c, d = n.x, n.y, n.z, -n.x*p2.x-n.y*p2.y-n.z*p2.z	#平面方程ax+by+cz+d=0
	t = -(a*p1.x + b*p1.y + c*p1.z + d) / (a*d1.x + b*d1.y + c*d1.z)	#直线与平面相交位置
	return t
#===============================================================================
# 类
#===============================================================================
@ti.data_oriented
class C光线:
	def __init__(self, a位置: t向量3, a方向: t向量3):
		self.m位置 = a位置
		self.m方向 = a方向
	@ti.func
	def at(self, t: float):
		return self.m位置 + self.m方向 * t
@ti.data_oriented
class I物体:
	@ti.func
	def f计算(self, a物理参数, dt):
		pass
	@ti.func
	def f更新(self):
		pass