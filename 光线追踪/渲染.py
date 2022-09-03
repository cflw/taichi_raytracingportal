import taichi as ti
from .公共 import *
#渲染参数
c采样数 = 16	#每像素光线数
c最大深度 = 50
c半深度 = c最大深度 // 2
c表面采样 = True
c继续概率 = 0.9
c模糊率 = 0.4
#渲染计算
@ti.data_oriented
class C渲染目标:
	def __init__(self, a宽度, a高度):
		self.m宽度 = a宽度
		self.m高度 = a高度
		self.m图像 = t向量3.field(shape = (a宽度, a高度))
@ti.data_oriented
class C渲染:
	def __init__(self, a渲染目标, a场景, a投射器, a光线染色 = None, a采样数 = c采样数):
		self.m目标 = a渲染目标
		self.m场景 = a场景
		self.m投射 = a投射器
		self.m光线染色 = a光线染色 if a光线染色 else C染色_光线追踪()
		self.m采样数 = a采样数
	@ti.kernel
	def f渲染(self):
		for i, j in self.m目标.m图像:
			v颜色 = t向量3(0, 0, 0)
			for k in range(self.m采样数):
				u = (i + ti.random()) / self.m目标.m宽度
				v = (j + ti.random()) / self.m目标.m高度
				v光线 = self.m投射.f取光线(u, v)
				v颜色 += self.m光线染色.f光线染色(self.m场景, v光线, i, j)
			self.m目标.m图像[i, j] = v颜色 / self.m采样数
#===============================================================================
# 渲染方法
#===============================================================================
@ti.data_oriented
class C染色_物体颜色:
	def __init__(self):
		pass
	@ti.func
	def f光线染色(self, a场景, a光线, x, y):
		v光线位置 = a光线.m位置
		v光线方向 = a光线.m方向
		v光线颜色 = t向量3(0, 0, 0)
		v碰撞, v交点, v交点法线, v前面, v发光颜色, v反射颜色, v材质 = a场景.f光线碰撞(C光线(v光线位置, v光线方向))
		if v碰撞:
			v光线颜色 = v发光颜色 + v反射颜色
		return v光线颜色
@ti.data_oriented
class C染色_朗伯反射:
	def __init__(self, a光源: t向量3):
		self.m光源 = a光源
	@ti.func
	def f光线染色(self, a场景, a光线, x, y):
		v光线位置 = a光线.m位置
		v光线方向 = a光线.m方向
		v光线颜色 = t向量3(0, 0, 0)
		v碰撞, v交点, v交点法线, v前面, v发光颜色, v反射颜色, v材质 = a场景.f光线碰撞(C光线(v光线位置, v光线方向))
		if v碰撞:
			if v材质 == E材质.e光源:
				v光线颜色 = v发光颜色 + v反射颜色
			else:
				v到光源 = (self.m光源 - v交点).normalized()
				v光线颜色 = v发光颜色 + v反射颜色 * ti.max(v到光源.dot(v交点法线) / v到光源.norm() * v交点法线.norm(), 0.0)
		return v光线颜色
@ti.data_oriented
class C染色_光线追踪:
	def __init__(self, a宽度, a高度):
		self.ma发光颜色 = t向量3.field(shape = (a宽度, a高度, c最大深度))	#太极不支持在太极函数内定义静态数组，先用场代替
		self.ma反射颜色 = t向量3.field(shape = (a宽度, a高度, c最大深度))
	@ti.func
	def f光线染色(self, a场景, a光线, x, y):	#光线追踪
		v当前深度 = 0
		v光线位置 = a光线.m位置
		v光线方向 = a光线.m方向
		v碰撞, v交点, v交点法线, v前面, v发光颜色, v反射颜色, v材质 = a场景.f光线碰撞(C光线(v光线位置, v光线方向))
		while v碰撞:
			d = v当前深度
			self.ma发光颜色[x, y, d] = v发光颜色
			self.ma反射颜色[x, y, d] = v反射颜色
			#结束条件
			v当前深度 += 1
			if v当前深度 > c半深度 and ti.random() > c继续概率:
				self.ma反射颜色[x, y, d] /= c继续概率
				break
			elif v当前深度 > c最大深度:
				break
			#根据材质决定如何反射光线
			if v材质 == E材质.e光源:
				break
			elif v材质 == E材质.e漫反射:
				v目标 = v交点 + v交点法线
				if c表面采样:
					v目标 += f随机单位向量()
				else:
					v目标 += f随机单位球体()
				v光线方向 = v目标 - v交点
				v光线位置 = v交点
			elif v材质 == E材质.e镜面反射:
				v光线方向 = f反射(v光线方向.normalized(), v交点法线)
				if v光线方向.dot(v交点法线) < 0:
					break
				v光线位置 = v交点
			elif v材质 == E材质.e折射:
				v折射率 = 1.5
				if v前面:
					v折射率 = 1 / v折射率
				cosθ = min(-v光线方向.normalized().dot(v交点法线), 1.0)
				sinθ = ti.sqrt(1 - cosθ * cosθ)
				if v折射率 * sinθ > 1 or f反射比(cosθ, v折射率) > ti.random():	#全反射
					v光线方向 = f反射(v光线方向.normalized(), v交点法线)
				else:	#折射
					v光线方向 = f折射(v光线方向.normalized(), v交点法线, v折射率)
				v光线位置 = v交点
			elif v材质 == E材质.e模糊反射:
				v光线方向 = f反射(v光线方向.normalized(), v交点法线)
				if c表面采样:
					v光线方向 += f随机单位向量() * c模糊率
				else:
					v光线方向 += f随机单位球体() * c模糊率
				if v光线方向.dot(v交点法线) < 0:
					break
				v光线位置 = v交点
			elif v材质 == E材质.e传送门:
				v光线位置 = v交点
				v光线方向 = v交点法线
			elif v材质 == E材质.e叠加:
				v光线位置 = v交点
				v光线方向 = v交点法线
			#新的循环
			v碰撞, v交点, v交点法线, v前面, v发光颜色, v反射颜色, v材质 = a场景.f光线碰撞(C光线(v光线位置, v光线方向))
		v光线颜色 = t向量3(1, 1, 1)
		if v当前深度 == 0:
			v光线颜色 = c背景色
		else:
			for i in range(v当前深度):
				d = v当前深度 - i - 1	#倒序
				v光线颜色 = self.ma发光颜色[x, y, d] + self.ma反射颜色[x, y, d] * v光线颜色
		return v光线颜色
