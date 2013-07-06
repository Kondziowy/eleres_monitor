# -*- coding: cp1250 -*-
"""
    signal_display - a simple widget that displays signal, voltage
    and temperature readings from an eLeReS RC radio. It can also draw graphs.

    Author: Konrad Brodzik (konrad.brodzik@gmail.com)
    
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
from Tkinter import *
from tkFont import *
from serial import *
from serial.tools import list_ports
import re
import tkMessageBox
import pdb

#https://github.com/matplotlib/matplotlib/downloads/
import matplotlib
matplotlib.use('TkAgg')

from numpy import arange
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

serial_port='COM8'
serial_speed=57600
update_interval=50
graph_drawing_period=5000
no_signal_timeout=2000

eleres_params=["RSSI","RCQ","U","T"]

param_dict={}

root = Tk()
big_font = Font(family="Arial",size="20")

class ReadingHolder:
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
        self._display_val_current=StringVar()
        self._values=ReadingHolder()
        self._canvas=''
        Label(root,text=label,font=big_font).grid(row=index,column=0)
        Label(root,font=big_font,textvariable=self._display_val).grid(row=index,column=1)
        self._cur_label=Label(root,font=big_font,textvariable=self._display_val_current)
        self._cur_label.grid(row=index,column=2)
        self._display_val.set("NO DATA")
        self._no_signal_timer=''

    def update_avg(self,value):
        self._display_val.set("%.2f" % (self._values.rolling_average(float(value)),))
        self._display_val_current.set("%.2f" % (float(value),))
        self._cur_label.config(foreground='black')
        if self._no_signal_timer != '':
                root.after_cancel(self._no_signal_timer)
        self._no_signal_timer=root.after(no_signal_timeout,self.no_signal)

    def no_signal(self):
        self._cur_label.config(foreground='red')
         
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
    ser.flushInput()
    line=ser.readline().replace("!","")
    print line
    for value in eleres_params:
        update_dashboard_value(value,line)
    root.after(update_interval,update_dashboard)

def update_dashboard_value(value,line):
    data=re.search(value+"=([0-9.-]*)",line)
    try:
        #print "%s %s" % (value,data.group(1))
        param_dict[value].update_avg(data.group(1))
    except:
        pass

def update_graph():
    param_dict["RSSI"].draw_graph()
    root.after(graph_drawing_period,update_graph)

def find_eleres():
    all_ports=list_ports.comports()
    for port in all_ports:
        print "Trying port %s" % port[0]
        try:
            ser = Serial(port[0], serial_speed, timeout=1)
            data = ser.read(10)
            if (len(data) > 0):
                print "Found LRS on %s" % port[0]
                return port[0]
        except:
            pass
        
    return "No transmitting LRS found"
        

def main():
    global ser
    global serial_port
    try:
        serial_port=find_eleres()
        ser = Serial(serial_port, serial_speed, timeout=1)
    except Exception,e:
        t="Could not open serial port %s, msg: %s" % (serial_port,e.message)
        tkMessageBox.showerror("Eleres dashboard",t)
        root.destroy()
        return 1
        
    for idx,param in enumerate(eleres_params):
        param_dict[param]=EleresParam(param,idx)
    update_dashboard()
    #root.after(graph_drawing_period,update_graph())
    root.mainloop()

if __name__ == '__main__':
    main()
