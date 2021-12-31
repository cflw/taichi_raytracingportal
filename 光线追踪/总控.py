from .公共 import *
class C总控:
	def __init__(self, a计算, a渲染, a输出):
		self.m计算 = a计算
		self.m渲染 = a渲染
		self.m输出 = a输出
	def run(self):
		print("开始")
		dt = c时间差 / c时间细分
		while self.m输出:
			for i in range(c时间细分):
				self.m计算.compute(dt)
			self.m渲染.paint()
			self.m输出.output()
		else:
			self.m输出.end()
		print("结束")