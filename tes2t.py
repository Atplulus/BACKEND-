import serial
import json
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime as dt
import time

class SerialPlotter:
    def __init__(self, root, port='/dev/ttyTHS1', baudrate=9600, timeout=1):
        self.root = root
        self.root.title("Speed Plotter")

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.running = False

        # Set up the plot
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.xdata = []
        self.ydata = []

        self.line, = self.ax.plot([], [], 'r-')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Speed')
        self.ax.set_title('Speed over Time')

        # Set up start/stop button
        self.start_button = ttk.Button(root, text="Start", command=self.start_reading)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_reading)
        self.stop_button.pack(side=tk.LEFT)

        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=1000, blit=True)

    def start_reading(self):
        if not self.running:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                self.running = True
                self.read_data()
            except serial.SerialException as e:
                print(f"Serial error: {e}")

    def stop_reading(self):
        if self.running:
            self.running = False
            if self.ser:
                self.ser.close()

    def read_data(self):
        if self.running and self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').strip()
            try:
                data = json.loads(line)
                unit = data.get("unit")
                speed = float(data.get("speed", 0))
                timestamp = time.time()  # Use Unix timestamp

                self.xdata.append(timestamp)
                self.ydata.append(speed)
                if len(self.xdata) > 20:
                    self.xdata = self.xdata[-20:]
                    self.ydata = self.ydata[-20:]
                
            except json.JSONDecodeError:
                print("Received invalid JSON data")

        self.root.after(1000, self.read_data)

    def update_plot(self, frame):
        self.line.set_data(self.xdata, self.ydata)
        self.ax.relim()
        self.ax.autoscale_view()
        self.ax.set_xticklabels([dt.datetime.fromtimestamp(ts).strftime('%H:%M:%S') for ts in self.xdata])
        return self.line,

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialPlotter(root, port='/dev/ttyTHS1', baudrate=9600, timeout=1)
    root.mainloop()
