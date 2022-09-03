import taichi as ti
from .公共 import *
from .传送门 import *
c激光深度 = 3	#激光数量,最多迭代多少次
c激光半径 = 0.1	#默认半径
c激光颜色0 = t向量3(1.5, 1.5, 1.5)	#内部颜色
c激光颜色1 = t向量3(1.0, 0.0, 0.0)	#边缘颜色
t激光分段 = ti.types.struct(
	m位置 = t向量3,
	m方向 = t向量3,
)
@ti.data_oriented
class C激光:	#激光自身有计算,不会参与物体间碰撞
	def __init__(self, a位置: t向量3, a方向: t向量3, a颜色: t向量3 = c激光颜色1, a半径: float = c激光半径):
		self.m位置 = self.m尾位置 = f新建场(t向量3, a位置)
		self.m方向 = self.m尾方向 = f新建场(t向量3, a方向)
		self.m激活 = self.m尾激活 = f新建场(bool, True)	#总是激活
		self.m颜色 = a颜色
		self.m半径 = a半径
		self.m碰撞 = False
		#添加激光节点
		self.ma节点 = []
		v上级 = self
		for i in range(c激光深度):
			v节点 = C激光节点(v上级, i)
			self.ma节点.append(v节点)
			v上级 = v节点
	def f计算(self, a物理参数, dt):
		pass
	def f更新(self):
		pass
@ti.data_oriented
class C激光节点(I物体):	#激光节点参与物体间碰撞,每个节点独立计算
	def __init__(self, a激光, a深度):
		self.m颜色 = a激光.m颜色
		self.m半径 = a激光.m半径
		self.m位置 = f新建场(t向量3)
		self.m方向 = f新建场(t向量3)
		self.m尾位置 = f新建场(t向量3)	#后节点的位置
		self.m尾方向 = f新建场(t向量3)	#后节点的方向
		self.t = f新建场(float)	#判断物体碰撞时的t,表示激光结束位置,不是光线碰撞的t
		self.m上级 = a激光	#前节点
		self.m深度 = a深度	#当前节点深度,从0开始
		self.m激活 = f新建场(bool)	#激活才能计算
		self.m尾激活 = f新建场(bool)
		self.m碰撞 = True
	@ti.func
	def f光线碰撞(self, a光线, a最小值, a最大值):
		#思路:把激光看作2d贴图,不考虑激光体积,计算光线与贴图碰撞
		v交点 = t向量3(0, 0, 0)
		v颜色 = c激光颜色0
		v碰撞 = False
		t = 0.0
		#计算两条直线最短距离位置
		d = f异面直线距离(a光线.m位置, a光线.m方向, self.m位置[None], self.m方向[None])
		if d <= c激光半径:	#相交
			t2 = f异面直线最近位置(self.m位置[None], self.m方向[None], a光线.m位置, a光线.m方向)	#交点在激光范围内
			if t2 > 0 and t2 < self.t[None]:
				t = f异面直线最近位置(a光线.m位置, a光线.m方向, self.m位置[None], self.m方向[None])	#确定相交位置
				v交点 = a光线.at(t)
				if t > a最小值 and t < a最大值:
					v碰撞 = True
					if d <= c激光半径 * 0.5:
						#v颜色 = c激光颜色0
						pass
					elif d <= c激光半径 * 0.75:
						v颜色 = lerp(c激光颜色0, self.m颜色, (d - c激光半径 * 0.5) / c激光半径 * 4)
					else:	#d > c激光半径
						v颜色 = lerp(self.m颜色, c黑, (d - c激光半径 * 0.75) / c激光半径 * 4)
		return v碰撞, t, v交点, -a光线.m方向, True, v颜色, c反射颜色, E材质.e叠加
	@ti.func
	def f计算(self, a物理参数, dt):
		#没有物理计算,只有更新状态
		self.m激活[None] = self.m上级.m尾激活[None]
		if self.m激活[None]:
			self.m位置[None] = self.m上级.m尾位置[None]
			self.m方向[None] = self.m上级.m尾方向[None]
		self.t[None] = c最大值	#每帧重置t
	@ti.func
	def f在(self, t):
		return self.m位置[None] + self.m方向[None] * t