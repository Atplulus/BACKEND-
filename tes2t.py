import tkinter as tk
from tkinter import ttk
import serial
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import threading

class SerialPlotter:
    def __init__(self, root, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        self.root = root
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.times = []
        self.speeds = []
        
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot_date(self.times, self.speeds, '-')

        self.canvas = plt.backends.backend_tkagg.FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.ani = FuncAnimation(self.fig, self.update_plot, interval=1000)

        self.start_serial_thread()

    def start_serial_thread(self):
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def read_serial_data(self):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    try:
                        data = json.loads(line)
                        speed = data.get("speed")
                        if speed is not None:
                            self.times.append(datetime.now())
                            self.speeds.append(speed)
                            if len(self.times) > 100:
                                self.times.pop(0)
                                self.speeds.pop(0)
                    except json.JSONDecodeError:
                        print("Received invalid JSON data")
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    def update_plot(self, frame):
        self.line.set_data(self.times, self.speeds)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Real-Time Serial Plotter")
    app = SerialPlotter(root, port='/dev/ttyUSB0', baudrate=9600, timeout=1)
    root.mainloop()
