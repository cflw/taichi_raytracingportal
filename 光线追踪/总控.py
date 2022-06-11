from .公共 import *
class C总控:
	def __init__(self, a计算, a渲染, a输出):
		self.m计算 = a计算
		self.m渲染 = a渲染
		self.m输出 = a输出
	def f运行(self):
		print("开始")
		dt = c时间差 / c时间细分
		while self.m输出:
			for i in range(c时间细分):
				self.m计算.f计算(dt)
			self.m渲染.f渲染()
			self.m输出.f输出()
		else:
			self.m输出.f结束()
		print("结束")