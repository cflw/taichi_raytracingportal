import taichi as ti
from .公共 import *
@ti.data_oriented
class C墙壁:	#竖起来的墙
	def __init__(self, a位置: t向量3, a尺寸: t向量2, a旋转: float, a颜色: t向量3, a材质, a双面渲染 = False, a碰撞 = True):
		self.m位置 = a位置
		self.m半尺寸 = a尺寸 * 0.5
		self.m旋转 = float(a旋转)	#简化计算,绕y轴旋转
		self.m颜色 = a颜色
		self.m材质 = a材质
		self.m双面渲染 = a双面渲染
		self.m碰撞 = a碰撞
	@ti.func
	def f光线碰撞(self, a光线, a最小值, a最大值):
		#旋转世界,把图片放置于y-z平面
		c = ti.cos(-self.m旋转)
		s = ti.sin(-self.m旋转)
		v旋转矩阵 = ti.Matrix([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
		v相对位置 = a光线.m位置 - self.m位置
		v相对位置 = v旋转矩阵 @ v相对位置
		v相对方向 = v旋转矩阵 @ a光线.m方向
		#计算相交
		v碰撞 = False
		t = 0.0
		v交点 = t向量3(0.0, 0.0, 0.0)
		v交点法线 = t向量3(0.0, 0.0, 0.0)
		v前面 = False
		if not self.m双面渲染 and v相对位置.x < 0:
			pass
		elif v相对方向.x == 0:
			pass
		else:
			#有2种情况:
			#1:相对位置是负,为了相交,相对方向应该是正的
			#2:相对位置是正,为了相交,相对方向应该是负的
			t = -v相对位置.x / v相对方向.x	#如果存在相交的情况,t应该是正的
			v相对交点 = v相对位置 + v相对方向 * t
			if t <= a最小值 or t >= a最大值:
				pass
			elif abs(v相对交点.z) < self.m半尺寸.x and abs(v相对交点.y) < self.m半尺寸.y:	#交点在矩形内
				v碰撞 = True
				v交点 = a光线.at(t)
				v交点法线 = t向量3(c, 0.0, s)
				if v相对位置.x >= 0:
					v前面 = True
				else:
					v交点法线 = -v交点法线
		return v碰撞, t, v交点, v交点法线, v前面, self.m颜色, self.m材质
@ti.data_oriented
class C地板:	#也可当天花板用
	def __init__(self, a位置: t向量3, a尺寸: t向量2, a颜色: t向量3, a材质, a天花板 = False, a双面渲染 = False, a碰撞 = True):
		self.m位置 = a位置
		self.m半尺寸 = a尺寸 * 0.5
		self.m颜色 = a颜色
		self.m材质 = a材质
		self.m天花板 = a天花板
		self.m双面渲染 = a双面渲染
		self.m碰撞 = a碰撞
	@ti.func
	def f光线碰撞(self, a光线, a最小值, a最大值):
		v相对位置 = a光线.m位置 - self.m位置
		v碰撞 = False
		t = 0.0
		v交点 = t向量3(0.0, 0.0, 0.0)
		v交点法线 = t向量3(0.0, 0.0, 0.0)
		v前面 = False
		if not self.m双面渲染 and ((v相对位置.y > 0) if self.m天花板 else (v相对位置.y < 0)):
			pass
		elif a光线.m方向.y == 0:
			pass
		else:
			t = -v相对位置.y / a光线.m方向.y
			v相对交点 = v相对位置 + a光线.m方向 * t
			if t <= a最小值 or t >= a最大值:
				pass
			elif abs(v相对交点.x) < self.m半尺寸.x and abs(v相对交点.z) < self.m半尺寸.y:	#交点在矩形内
				v碰撞 = True
				v交点 = a光线.at(t)
				if v相对位置.y >= 0:	#光线在上
					v前面 = True
					v交点法线 = t向量3(0.0, 1.0, 0.0)
				else:
					v交点法线 = t向量3(0.0, -1.0, 0.0)
		return v碰撞, t, v交点, v交点法线, v前面, self.m颜色, self.m材质
			
