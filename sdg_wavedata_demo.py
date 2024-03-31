#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa as visa
import time
import binascii

#resource of Device
device_resource = 'USB0::0xF4EC::0x1102::SDG2XCAX5R1798::INSTR'


#Little endian, 16-bit 2's complement

#send 10 points to the generator. hex(-32768)= 0X8000, hex(-16134)=0XC0FA, hex(0)=0X0000, hex(16134)=0X3F06, hex(32767)=0X7FFF

data_points = [0x8000,0x8000,0xc0fa, 0x0000 ,0x3F06, 0x7fff,0x7fff,0x7fff]

wave_points =[]
for i in range(240):

    wave_points.append(data_points[i%8])

print(len(wave_points))

def create_wave_file():
    """create a file"""
    f = open("wave.bin", "wb")
    for a in wave_points:
        b = hex(a)
        b = b[2:]
        len_b = len(b)
        if (0 == len_b):
            b = '0000'
        elif (1 == len_b):
            b = '000' + b
        elif (2 == len_b):
            b = '00' + b
            print(b)
        elif (3 == len_b):
            b = '0' + b
        b = b[2:4] + b[:2]
        print(b)

        c = binascii.unhexlify(b)
        #Hexadecimal integer to ASCii encoded string
        f.write(c)
    f.close()

def send_wave_data(dev):
    """send testwave1.bin to the device"""
    f = open("wave.bin", "rb")    #wave.bin is the waveform to be sent
    data = f.read().decode("latin1")
    print('write class:', type(data))
    print('write bytes:',len(data))
    dev.write_termination = ''
    print("Start................")
    time.sleep(0.5)
    time_a = time.time()
    dev.write("C1:WVDT WVNM,SINE1,FREQ,2000,AMPL,1.0,OFST,0.0,PHASE,0.0,WAVEDATA,%s"%(data),encoding='latin1')    #"X" series (SDG1000X/SDG2000X/SDG6000X/X-E)
    # isOperationFinish(dev)
    time_temp = time.time()
    dev.write("C1:ARWV NAME,SINE1")
    # isOperationFinish(dev) #调用函数
    time_b = time.time()

    print("Stop..............")

    f.close()
    time.sleep(3)

    return data

def get_wave_data(dev):
    """get wave from the devide"""
    dev.read_termination = ''
    f = open("wave.bin", "wb")    #save the waveform as wave.bin
    # dev.write("WVDT? M1")    #"X" series (SDG1000X/SDG2000X/SDG6000X/X-E)
    dev.write("WVDT? USER, urat")
    time.sleep(1)
    data = dev.read(encoding='latin1')
    print("data length=",len(data))
    data_pos = data.find("WAVEDATA,") + len("WAVEDATA,")
    print('pos::::',data_pos)
    print( data[0:data_pos])
    wave_data = data[data_pos:-1]
    print('read bytes:',len(wave_data))
    f.write(wave_data.encode('latin1'))
    f.close()
    return wave_data

def sdg_write(device, command):
    device.write('VKEY VALUE,KB_{},STATE,1'.format(command))

def sdg_delete(sdg):
    sdg_write(sdg, 'UTILITY')
    sdg_write(sdg, 'FUNC1')
    sdg_write(sdg, 'FUNC4')
    sdg.write('BUZZ OFF') #Turn on the buzzer to indicate that deletion is complete
    sdg_write(sdg, 'STORE_RECALL') #Start deleting
    for i in range(4):
        sdg_write(sdg, 'KNOB_RIGHT')

        time.sleep(0.04)
        sdg_write(sdg, 'KNOB_RIGHT')
        time.sleep(0.04)
        sdg_write(sdg, 'FUNC5')
        time.sleep(0.04)
        sdg_write(sdg, 'FUNC5')
        time.sleep(2)



if __name__ == '__main__':
    """"""
    #device = visa.instrument(device_resource, timeout=30*60*1000, chunk_size = 16*1024*1025)
    rm=visa.ResourceManager()
    device=rm.open_resource(device_resource, timeout=50000, chunk_size = 30*1024*1024)
    device.write_termination = ''
    device.read_termination = ''
    create_wave_file()
    for i in range(1):
        send=send_wave_data(device)

