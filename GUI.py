# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui, uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import sys
from PyQt5.QtWidgets import *
import numpy as np
import binascii
import pyvisa as visa
import time
from math import *
matplotlib.use('Qt5Agg')


def d2intb(decimal_num, num_bits):
    if decimal_num >= 0:
        binary_str = bin(decimal_num)[2:].zfill(num_bits)
    else:
        positive_value = abs(decimal_num)
        inverted_value = (1 << num_bits) - positive_value
        binary_str = bin(inverted_value)[2:]
    return binary_str


def intb2h(binary_str):
    decimal_num = int(binary_str, 2)
    hex_str = hex(decimal_num)[2:].upper()
    return hex_str


def d2inth(decimal_num, num_bits):
    hex_str = intb2h(d2intb(decimal_num, num_bits))
    return hex_str


def fill_16(hexnum):
    b = hexnum
    len_b = len(b)
    if (0 == len_b):
        b = '0000'
    elif (1 == len_b):
        b = '000' + b
    elif (2 == len_b):
        b = '00' + b
    elif (3 == len_b):
        b = '0' + b
    b = b[2:4] + b[:2]
    return b


def h2ascii(hex16):
    return binascii.unhexlify(hex16)


def wave_file_create(file_name, wave_data):
    f = open(file_name, "wb")
    wave_data=wave_data/np.max(np.abs(wave_data))*32767
    for a in wave_data:
        f.write(h2ascii(fill_16(d2inth(int(a), 16))))
    f.close


def dev_list_get():
    rm = visa.ResourceManager()  # 打开资源设备管理器
    devs = rm.list_resources_info("?*::INSTR")
    out = list(devs.keys())
    if len(out) <= 0:
        print("There is no devs")
    return out


def wave_data_send(dev, CH, data, data_name, freq, ampl):
    print('write class:', type(data))
    print('write bytes:', len(data))
    dev.write_termination = ''
    print("Start................")
    time.sleep(0.5)
    op = CH+":WVDT WVNM,"+data_name+",FREQ,"+freq+",AMPL," + \
        ampl+",OFST,0.0,PHASE,0.0,WAVEDATA,%s" % (data)
    dev.write(op, encoding='latin1')
    time.sleep(0.5)
    dev.write(CH+":ARWV NAME,"+data_name)
    print("Stop..............")

def wave_data_get(dev):
    #暂未验证
    dev.read_termination = ''
    f = open("temp_get.bin", "wb")
    # dev.write("WVDT? M1")    #"X" series (SDG1000X/SDG2000X/SDG6000X/X-E)
    dev.write("WVDT? USER, urat")
    time.sleep(1)
    data = dev.read(encoding='latin1')
    print("data length=",len(data))
    data_pos = data.find("WAVEDATA,") + len("WAVEDATA,")
    print('pos::::',data_pos)
    #print( data[0:data_pos])
    wave_data = data[data_pos:-1]
    print('read bytes:',len(wave_data))
    f.write(wave_data.encode('latin1'))
    f.close()
    return wave_data

class mainwindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # PyQt5
        self.ui = uic.loadUi("./GUI.ui")
        self.ui.calc.clicked.connect(self.calc_handel_click)
        self.ui.save_pushButton.clicked.connect(self.save_click)
        self.ui.read_pushButton.clicked.connect(self.read_click)
        self.ui.dev_refresh.clicked.connect(self.dev_refresh_click)
        self.ui.upload_pushButton.clicked.connect(self.upload_click)
        self.ui.CH1_out_pushButton.clicked.connect(self.CH1_out_click)
        self.ui.CH1_out_pushButton_2.clicked.connect(self.CH1_off_click)
        self.ui.CH2_out_pushButton.clicked.connect(self.CH2_out_click)
        self.ui.CH2_out_pushButton_2.clicked.connect(self.CH2_off_click)
        self.ui.CH_out_pushButton.clicked.connect(self.CH_out_click)
        self.ui.CH_out_pushButton_2.clicked.connect(self.CH_off_click)
        dev_list = dev_list_get()
        self.ui.dev_comboBox.addItems(dev_list)
        if len(dev_list)<=0 :
            print("There is no devs")
        else:
            rm = visa.ResourceManager()
            device_resource = self.ui.dev_comboBox.currentText()
            dev = rm.open_resource(
                device_resource, timeout=50000, chunk_size=1*1024)
            # 默认50欧输出
            dev.write("C1:OUTP LOAD,50")
            dev.write("C2:OUTP LOAD,50")

    def CH_get(self):
        if self.ui.CH_comboBox.currentText() == "CH1":
            return "C1"
        else:
            return "C2"

    def data_len_get(self):
        if self.ui.data_len.text() == "":
            return 1200
        elif int(self.ui.data_len.text())<0:
            QMessageBox.information(self, "提示", "数据长度大于等于0")
            return 1200
        else:
            return int(self.ui.data_len.text())

    def f_repeat_get(self):
        if self.ui.f_repeat.text() == "":
            return 1000
        elif int(self.ui.f_repeat.text())<0:
            QMessageBox.information(self, "提示", "重复频率大于等于0")
            return 1000
        else:
            return int(self.ui.f_repeat.text())
    def ampl_get(self):
        amp_=self.ui.data_amp.text()
        if amp_ == "":
            return 1.0
        elif float(amp_)<0:
            QMessageBox.information(self, "提示", "幅值大于等于0")
            return 1.0
        elif float(amp_)>4:
            QMessageBox.information(self, "提示", "幅值不超过4")
            return 4
        else:
            return float(amp_)
    def expr_get(self):
        if self.ui.expr_plainTextEdit.toPlainText() == "":
            return "sin(2*pi*x)"
        else:
            return self.ui.expr_plainTextEdit.toPlainText()

    def calc_handel_click(self):
        xmin, xmax = 0, 1
        try:
            L = self.data_len_get()
            x_values = np.linspace(xmin, xmax-1/L, L)
            expr_str = self.expr_get()
            global y_values
            y_values = []
            for x in x_values:
                y_values.append(eval(expr_str))
            self.ui.mplwidget.canvas.axes.clear()
            self.ui.mplwidget.canvas.axes.plot(x_values, y_values)
            self.ui.mplwidget.canvas.axes.set_xlabel('x')
            self.ui.mplwidget.canvas.axes.set_xlabel('y')
            self.ui.mplwidget.canvas.draw()
        except:
            QMessageBox.information(self, "提示", "表达式可能错误")

    def save_click(self):
        self.file_name, __ = QFileDialog.getSaveFileName(
            self, "文件保存", "./", "bin文件 (*.bin)")
        if str(self.file_name) == "":
            QMessageBox.information(self, "提示", "没有保存数据,请重新保存。")  # 调用弹窗提示
            return self.file_name
        else:
            wave_file_create(self.file_name, y_values)
            print("save file_name:"+self.file_name)
            self.ui.save_filename.setText(self.file_name)
            return self.file_name

    def read_click(self):
        self.read_file_name, __ = QFileDialog.getOpenFileName(
            self, "文件保存", "./", "bin文件 (*.bin)")
        if str(self.read_file_name) == "":
            QMessageBox.information(self, "提示", "数据,请重新保存或读取。")  # 调用弹窗提示
            return self.read_file_name
        else:
            self.ui.read_filename.setText(self.read_file_name)
            print("read file_name:"+self.read_file_name)
            f = open(self.read_file_name, "rb")
            self.data = f.read().decode("latin1")
            f.close()
            return self.read_file_name

    def upload_click(self):
        rm = visa.ResourceManager()
        device_resource = self.ui.dev_comboBox.currentText()
        dev = rm.open_resource(
            device_resource, timeout=50000, chunk_size=30*1024*1024)
        CH = self.CH_get()
        data_name = self.ui.data_name.text() if self.ui.data_name.text() != "" else "temp"
        freq = str(self.f_repeat_get()*1000)
        ampl = str(self.ampl_get())
        self.ui.update_state.setText("上传状态:上传中...")
        if (self.ui.bin_checkBox.isChecked()):
            try:
                wave_file_create("./temp.bin", y_values)
                f = open("./temp.bin", "rb")
                data = f.read().decode("latin1")
                f.close()
                wave_data_send(dev, CH, data, data_name, freq, ampl)
                self.ui.update_state.setText("上传状态:上传完毕")
            except:
                self.ui.update_state.setText("上传状态:出错")
        else:
            try:
                wave_data_send(dev, CH, self.data, data_name, freq, ampl)
                self.ui.update_state.setText("上传状态:上传完毕")
            except:
                print("date error")
                self.ui.update_state.setText("上传状态:出错")

    def dev_refresh_click(self):
        dev_list = dev_list_get()
        self.ui.dev_comboBox.clear()
        self.ui.dev_comboBox.addItems(dev_list)

    def CH1_out_click(self):
        rm = visa.ResourceManager()
        device_resource = self.ui.dev_comboBox.currentText()
        dev = rm.open_resource(
            device_resource, timeout=50000, chunk_size=128*128)
        dev.write("C1:OUTP ON")

    def CH1_off_click(self):
        rm = visa.ResourceManager()
        device_resource = self.ui.dev_comboBox.currentText()
        dev = rm.open_resource(
            device_resource, timeout=50000, chunk_size=128*128)
        dev.write("C1:OUTP OFF")

    def CH2_out_click(self):
        rm = visa.ResourceManager()
        device_resource = self.ui.dev_comboBox.currentText()
        dev = rm.open_resource(
            device_resource, timeout=50000, chunk_size=128*128)
        dev.write("C2:OUTP ON")

    def CH2_off_click(self):
        rm = visa.ResourceManager()
        device_resource = self.ui.dev_comboBox.currentText()
        dev = rm.open_resource(
            device_resource, timeout=50000, chunk_size=128*128)
        dev.write("C2:OUTP OFF")

    def CH_out_click(self):
        rm = visa.ResourceManager()
        device_resource = self.ui.dev_comboBox.currentText()
        dev = rm.open_resource(
            device_resource, timeout=50000, chunk_size=128*128)
        dev.write("C1:OUTP ON")
        dev.write("C2:OUTP ON")

    def CH_off_click(self):
        rm = visa.ResourceManager()
        device_resource = self.ui.dev_comboBox.currentText()
        dev = rm.open_resource(
            device_resource, timeout=50000, chunk_size=128*128)
        dev.write("C1:OUTP OFF")
        dev.write("C2:OUTP OFF")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainwindow()
    window.ui.show()
    sys.exit(app.exec_())
