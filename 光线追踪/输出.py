import taichi as ti
from .公共 import *
#渲染输出
@ti.data_oriented
class C窗口:
	def __init__(self, a渲染目标, a窗口标题 = "光线追踪"):
		self.m渲染目标 = a渲染目标
		self.m窗口 = ti.ui.Window(a窗口标题, res = (a渲染目标.m宽度, a渲染目标.m高度))
		self.m画布 = self.m窗口.get_canvas()
	def __bool__(self):
		return self.m窗口.running
	def output(self):
		self.m画布.set_image(self.m渲染目标.m图像)
		self.m窗口.show()
	def end(self):
		pass
@ti.data_oriented
class C视频:
	def __init__(self, a渲染目标, a文件名, a渲染帧数):
		self.m渲染目标 = a渲染目标
		self.m视频管理 = ti.VideoManager(output_dir = a文件名, framerate = 60)
		self.m渲染帧数 = a渲染帧数
		self.m当前帧数 = 0
	def __bool__(self):
		return self.m当前帧数 < self.m渲染帧数
	def output(self):
		self.m视频管理.write_frame(self.m渲染目标.m图像)
		self.m当前帧数 += 1
		if self.m当前帧数 % 100 == 0:	#整百的时候输出一次进度
			print(f"{self.m当前帧数 / self.m渲染帧数 * 100}%")
	def end(self):
		self.m视频管理.make_video(gif = False, mp4 = True)
		print(f"保存到 {self.m视频管理.get_output_filename('')}")
