import taichi as ti
from .公共 import *
@ti.data_oriented
class C场景:	#存放物体
	def __init__(self):
		self.ma物体 = []
		self.ma镜像 = []
	def f添加(self, a物体):
		self.ma物体.append(a物体)
		#对于可以穿过门的物体,创建镜像,再添加到镜像列表
		if hasattr(a物体, "f镜像"):
			self.ma镜像.append(a物体.f镜像())
	@ti.func
	def f光线碰撞(self, a光线):	#计算光与哪个物体相交,返回物体属性
		v距离 = c最大值
		v碰撞 = False
		v交点 = t向量3(0, 0, 0)
		v交点法线 = t向量3(0, 0, 0)
		v前面 = False
		v颜色 = t向量3(0, 0, 0)
		v材质 = E材质.e漫反射
		for i in ti.static(range(len(self.ma物体))):
			v碰撞0, v距离0, v交点0, v交点法线0, v前面0, v颜色0, v材质0 = self.ma物体[i].f光线碰撞(a光线, c最小值, v距离)
			if v碰撞0:
				v距离 = v距离0
				v碰撞 = v碰撞0
				v距离 = v距离0
				v交点 = v交点0
				v交点法线 = v交点法线0
				v前面 = v前面0
				v颜色 = v颜色0
				v材质 = v材质0
		for i in ti.static(range(len(self.ma镜像))):
			if self.ma镜像[i].m物体.m靠近门[None] > 0:
				v碰撞0, v距离0, v交点0, v交点法线0, v前面0, v颜色0, v材质0 = self.ma镜像[i].f光线碰撞(a光线, c最小值, v距离)
				if v碰撞0:
					v距离 = v距离0
					v碰撞 = v碰撞0
					v距离 = v距离0
					v交点 = v交点0
					v交点法线 = v交点法线0
					v前面 = v前面0
					v颜色 = v颜色0
					v材质 = v材质0
		#返回
		return v碰撞, v交点, v交点法线, v前面, v颜色, v材质
