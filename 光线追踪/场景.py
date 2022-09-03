import taichi as ti
from .公共 import *
@ti.data_oriented
class C场景:	#存放物体
	def __init__(self):
		self.ma物体 = []	#所有物体
		self.ma可见物体 = []	#可以和光线交互的物体
		self.ma镜像物体 = []	#可以穿过传送门的物体的镜像
	def f添加(self, *aa物体):
		for v物体 in aa物体:
			self.ma物体.append(v物体)
			#可以和光线发生碰撞的物体加到可见物体列表
			if hasattr(v物体, "f光线碰撞"):
				self.ma可见物体.append(v物体)
			#对于可以穿过门的物体,创建镜像,再添加到镜像列表
			if hasattr(v物体, "f镜像"):
				self.ma镜像物体.append(v物体.f镜像())
	@ti.func
	def f光线碰撞(self, a光线):	#计算光与哪个物体相交,返回物体属性
		v距离 = c最大值
		v碰撞 = False
		v交点 = t向量3(0, 0, 0)
		v交点法线 = t向量3(0, 0, 0)
		v前面 = False
		v发光颜色 = c发光颜色
		v反射颜色 = c反射颜色
		v材质 = E材质.e漫反射
		for i in ti.static(range(len(self.ma可见物体))):
			v碰撞0, v距离0, v交点0, v交点法线0, v前面0, v颜色0, v颜色1, v材质0 = self.ma可见物体[i].f光线碰撞(a光线, c最小值, v距离)
			if v碰撞0:
				v距离 = v距离0
				v碰撞 = v碰撞0
				v距离 = v距离0
				v交点 = v交点0
				v交点法线 = v交点法线0
				v前面 = v前面0
				v发光颜色 = v颜色0
				v反射颜色 = v颜色1
				v材质 = v材质0
		for i in ti.static(range(len(self.ma镜像物体))):
			if self.ma镜像物体[i].m物体.m靠近门[None] > 0:
				v碰撞0, v距离0, v交点0, v交点法线0, v前面0, v颜色0, v颜色1, v材质0 = self.ma镜像物体[i].f光线碰撞(a光线, c最小值, v距离)
				if v碰撞0:
					v距离 = v距离0
					v碰撞 = v碰撞0
					v距离 = v距离0
					v交点 = v交点0
					v交点法线 = v交点法线0
					v前面 = v前面0
					v发光颜色 = v颜色0
					v反射颜色 = v颜色1
					v材质 = v材质0
		#返回
		return v碰撞, v交点, v交点法线, v前面, v发光颜色, v反射颜色, v材质
		#调试用:把t转换成颜色,观察距离
		# v距离颜色 = t向量3(v距离*0.1, v距离, v距离*10)
		# return v碰撞, v交点, v交点法线, v前面, c发光颜色, v距离颜色, v材质