# 太极图形课S1-大作业-光线追踪传送门

## 作业来源
灵感来源于游戏《传送门》，制作了包含一对传送门的实验室场景。

## 运行方式

#### 运行环境：
```
[Taichi] version 0.8.8, llvm 10.0.0, commit 7bae9c77, win, python 3.9.9
[Taichi] Starting on arch=cuda
```

#### 运行：
```
python 场景0.py
```

## 效果展示

（视频上传中）

![场景1](./data/001444.png)

## 整体结构

### 场景

* **场景0**：测试场景
* **场景1**：简单房间和一堆小球

### 光线追踪

核心

* **公共**：包含常量、函数
* **场景**：用来存储物体
* **物理**：处理物体间的碰撞
* **投影**：把三维场景投到二维屏幕
* **渲染**：计算光线
* **输出**：输出画面内容
* **总控**：把上面的内容合起来统一控制

物体

* **传送门**
* **球体**
* **矩形**

## 实现细节：

懒得写了，具体看《传送门》和《传送门2》的开发者注释吧

## 广告：自制地图

买了《传送门2》的小伙伴可以试一下我做的地图，地图已上传到创意工坊😝

https://steamcommunity.com/sharedfiles/filedetails/?id=1635313683