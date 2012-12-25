# -*- coding: cp1250 -*-

from Tkinter import *
from tkFont import *
from serial import *
import re
import tkMessageBox

#https://github.com/matplotlib/matplotlib/downloads/
import matplotlib
matplotlib.use('TkAgg')

from numpy import arange
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

serial_port='COM21'
serial_speed=57600
update_interval=100
graph_drawing_period=5000

eleres_params=["RSSI","RCQ","U","T"]

param_dict={}

root = Tk()
big_font = Font(family="Arial",size="20")

class ValueHolder:
    def __init__(self):
        self.values=[]
        self._count=0
    def rolling_average(self,new_value):
        self.values.append(new_value)
        self._count+=1
        if self._count > 10:
            self.values.pop(0)
            self._count=10
        return sum(self.values)/self._count

class EleresParam:
    def __init__(self,label,index):
        self._display_val=StringVar()
        self._values=ValueHolder()
        self._canvas=''
        Label(root,text=label,font=big_font).grid(row=index,column=0)
        Label(root,font=big_font,textvariable=self._display_val).grid(row=index,column=1)
        self._display_val.set("NO DATA")

    def update_avg(self,value):
        self._display_val.set("%.2f" % (self._values.rolling_average(float(value)),))

    def draw_graph(self):
        if self._canvas == '':
            f = Figure(figsize=(3,2), dpi=100)
            self._subplot = f.add_subplot(111)    
            self._canvas = FigureCanvasTkAgg(f, master=root)
            self._canvas.show()
            self._canvas.get_tk_widget().grid(row=5)
        s = self._values.values
        t = arange(0,len(s),1)
        self._subplot.clear()
        self._subplot.plot(t,s)
        self._canvas.draw()
        
        
def update_dashboard():
    line = ser.readline()
    for value in eleres_params:
        update_dashboard_value(value,line)
    root.after(update_interval,update_dashboard)

def update_dashboard_value(value,line):
    data=re.search(value+"=([0-9.]*)",line)
    try:
        print "%s %s" % (value,data.group(1))
        param_dict[value].update_avg(data.group(1))
    except:
        pass

def update_graph():
    param_dict["RSSI"].draw_graph()
    root.after(graph_drawing_period,update_graph)

def main():
    global ser
    try:
        ser = Serial(serial_port, serial_speed, timeout=1)
    except:
        t="Could not open serial port %s" % (serial_port,)
        tkMessageBox.showerror("Eleres dashbaord",t)
        root.quit()
        
    for idx,param in enumerate(eleres_params):
        param_dict[param]=EleresParam(param,idx)
    update_dashboard()
    root.after(graph_drawing_period,update_graph())
    root.mainloop()

if __name__ == '__main__':
    main()
