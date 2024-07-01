import sys
import serial
import json
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QTextEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer

class RealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Real-time Speed Plot')
        self.setGeometry(100, 100, 1200, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.plot_widget = pg.PlotWidget(title='Real-time Speed Plot')
        self.plot_widget.showGrid(x=True, y=True)
        self.layout.addWidget(self.plot_widget)

        self.controls_layout = QHBoxLayout()
        self.layout.addLayout(self.controls_layout)

        self.api_command_label = QLabel("API Command:")
        self.api_command_entry = QLineEdit()
        self.send_button = QPushButton('Send')
        self.reset_button = QPushButton('Reset')

        self.controls_layout.addWidget(self.api_command_label)
        self.controls_layout.addWidget(self.api_command_entry)
        self.controls_layout.addWidget(self.send_button)
        self.controls_layout.addWidget(self.reset_button)

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.layout.addWidget(self.terminal_output)

        self.send_button.clicked.connect(self.send_command)
        self.reset_button.clicked.connect(self.reset_plot)

        self.speed_data = []
        self.time_data = []
        self.index = 0

        self.serial_port = '/dev/ttyTHS1'  # Replace with your serial port
        self.baud_rate = 9600              # Replace with your baud rate
        self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
        self.reading_active = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_sensor_data)

    def send_command(self):
        api_command = self.api_command_entry.text()
        if api_command:
            self.ser.write(api_command.encode() + b'\n')
            self.terminal_output.append(f"Sent: {api_command}")

        if not self.reading_active:
            self.reading_active = True
            self.timer.start(1000)  # Read data every second

    def read_sensor_data(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').strip()

            if line:
                try:
                    self.terminal_output.append(f"Received: {line}")
                    data = json.loads(line)
                    if "speed" in data:
                        speed = float(data["speed"])
                        timestamp = time.time()  # Use Unix timestamp

                        self.speed_data.append(speed)
                        self.time_data.append(timestamp)

                        # Keep only the last 20 data points
                        if len(self.speed_data) > 20:
                            self.speed_data = self.speed_data[-20:]
                            self.time_data = self.time_data[-20:]

                        self.plot_widget.clear()
                        self.plot_widget.plot(self.time_data, self.speed_data, pen='c', name='Speed (km/h)')
                except json.JSONDecodeError:
                    self.terminal_output.append(f"Invalid JSON data: {line}")
                except ValueError as e:
                    self.terminal_output.append(f"ValueError: {e} - Data: {line}")

    def reset_plot(self):
        self.plot_widget.clear()
        self.speed_data.clear()
        self.time_data.clear()
        self.index = 0
        self.terminal_output.clear()
        self.reading_active = False
        self.timer.stop()
        self.terminal_output.append("Plot reset.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec_())
