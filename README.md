## 声明：本仓库未发表于Gitcode，并拒绝CSDN平台使用
## Siglent_AWG_GUI
鼎阳AWG的开源GUI上位机，由PYQT5设计，Visa通信，意在取代计算很慢的EasyWave

## 必要条件
1. Python<=3.8
2. visa 驱动
3. pyqt5
4. pyvisa
5. numpy
6. matplotlib

## 文件结构树
```
Siglent_AWG_GUI
│  GUI.py --GUI主程序
│  GUI.ui --GUI界面文件
│  LICENSE --许可文件
│  mplwidget.py --matplotlib绘图控件
│  README.md --说明文件
│  run.bat --运行命令
│  sdg_wavedata_demo.py --鼎阳py 官方demo
```


## 使用方法
- 打开run.bat，包含了运行命令
- 输入以x为变量的波形表达式，如：$\sin(2*pi*x)$，其中$x\in [0，1)$
- 设置波形长度、波形采样重复频率、波形幅度，点击开始计算波形
- *可选*：点击保存.bin文件，储存波形数据
- 选择对应设备，设置通道与波形名称，选择是否使用bin文件(若不使用则用目前计算的波形数据)，上传波形


## 注意事项
- 波形长度代表绘制的波形长度，DDS模式下，波形长度小于16K(SDG2000系列)或小于32K(SDG6000系列)；重复频率代表鼎阳AWG在DDS模式下绘制波形的重复频率，波形长度与重复频率的乘积小于等于采样率，AWG会自动插值或者抽值；幅度代表波形幅度
- 关于幅值：绘图区域显示的是表达式直接计算所得的值，额外设置的幅值代表最终由AWG输出的峰峰值，会采用归一化计算波形的方式对波形进行缩放，再由设置峰峰值输出
- 可用函数与常量：python的math库中的所有函数与常量
- **注意：由于使用了eval()，所以谨慎使用python语句作为表达式**

## TODO
- [x] 添加读取波形预览功能
- [ ] 添加波形回读功能
- [ ] 添加波形细化查看功能
- [ ] 添加基本波形设置与输出
