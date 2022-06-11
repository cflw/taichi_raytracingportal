import taichi as ti
ti.init(arch = ti.vulkan)
from .场景 import *
from .物理 import *
from .投影 import *
from .渲染 import *
from .输出 import *
from .总控 import *
#物体
from .传送门 import *
from .矩形 import *
from .球体 import *