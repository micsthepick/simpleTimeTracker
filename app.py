import sys
import argparse
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QLabel, QWidget
from PySide6.QtCore import QTimer
from datetime import datetime, timedelta
from plyer import notification


class SimpleTimeTracker(QMainWindow):
    def __init__(self, break_interval=30):
        super().__init__()
        
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.log_file_path = f"time_tracker_log_{current_date}.txt"


        # Window settings
        self.setWindowTitle("Simple Time Tracker")
        self.setGeometry(100, 100, 400, 300)

        # Layout and Widgets
        layout = QVBoxLayout()
        
        self.timer_display = QLabel("00:00:00", self)
        
        font = self.timer_display.font()
        font.setPointSize(20)  # Adjust the size as needed
        font.setBold(True)
        self.timer_display.setFont(font)
        self.timer_display.setStyleSheet("color: black")  # black when inactive, red when active


        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_timer)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_timer)

        self.lap_button = QPushButton("Lap", self)
        self.lap_button.clicked.connect(self.record_lap)

        self.description = QTextEdit(self)
        self.description.setPlaceholderText("Type a quick description of what is being undertaken...")

        self.log = QTextEdit(self)
        #self.log.setReadOnly(True)
        ## allow backloging and correction

        layout.addWidget(self.description)
        layout.addWidget(self.timer_display)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.lap_button)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log)
        
        self.description.setFixedHeight(60)  # Adjust the value as needed
        
        # Set stretch factors
        layout.setStretchFactor(self.description, 0)
        layout.setStretchFactor(self.timer_display, 0)
        layout.setStretchFactor(self.start_button, 0)
        layout.setStretchFactor(self.stop_button, 0)
        layout.setStretchFactor(self.lap_button, 0)
        layout.setStretchFactor(self.log, 1)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Timer setup
        self.break_interval = timedelta(minutes=break_interval)
        self.timer_interval = 1000  # 1 second in milliseconds

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_display)
        self.timer_running = False
        
    def write_log_to_file(self):
        with open(self.log_file_path, 'w') as file:
            file.write(self.log.toPlainText())
            
    def closeEvent(self, event):
        if self.timer_running:
            self.stop_timer()
        self.write_log_to_file()
        event.accept()

    def format_seconds(self, total_seconds: int) -> str:
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def update_timer_display(self):
        if not self.timer_running:
            return
        time_now = datetime.now()
        self.elapsed_time_raw = time_now - self.start_time
        self.elapsed_time_seconds = self.elapsed_time_raw.seconds
        formatted_time = self.format_seconds(self.elapsed_time_seconds)
        self.timer_display.setText(formatted_time)

        if (time_now - self.last_notification_time) >= self.break_interval:
            self.prompt_break()
            self.last_notification_time = time_now

    def format_timedelta(self, duration: timedelta) -> str:
        total_seconds = int(duration.total_seconds())
        return self.format_seconds(total_seconds)
        
    def _start_new_task(self):
        self.start_time = datetime.now()
        self.timer.start(self.timer_interval)
        self.saved_task = self.description.toPlainText()
        self.log.append(f"Started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}: {self.saved_task}")
        self.write_log_to_file()  # Write to file

    def _stop_current_task(self):
        self.timer.stop()
        end_time = datetime.now()
        duration = end_time - self.start_time
        formatted_duration = self.format_timedelta(duration)
        self.log.append(f"Ended at {end_time.strftime('%Y-%m-%d %H:%M:%S')} (Duration: {formatted_duration}): {self.saved_task}")
        self.write_log_to_file()  # Write to file

    def start_timer(self):
        if not self.timer_running:
            self.last_notification_time = datetime.now()
            self._start_new_task()
            self.timer_display.setStyleSheet("color: red")  # black when inactive, red when active
            self.timer_running = True

    def stop_timer(self):
        if self.timer_running:
            self._stop_current_task()
            self.timer_display.setStyleSheet("color: black")  # black when inactive, red when active
            self.timer_display.setText("00:00:00")
            self.timer_running = False
    
    def record_lap(self):
        if self.timer_running:
            self._stop_current_task()
            self._start_new_task()

    def prompt_break(self):
        # Send a desktop notification
        notification.notify(
            title='Simple Time Tracker',
            message='Time to check what you are doing, perhaps take a break?',
            app_name='SimpleTimeTracker',
            timeout=10  # Notification will be visible for 10 seconds
        )
        ##self.log.append("Time for a break!")
        ##self.write_log_to_file()  # Write to file

def parse_arguments():
    parser = argparse.ArgumentParser(description="Simple Time Tracker with configurable break intervals.")
    parser.add_argument('--break-interval', type=int, default=30,
                        help='Break interval in minutes. Default is 30 minutes.')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()
    app = QApplication(sys.argv)
    window = SimpleTimeTracker(break_interval=args.break_interval)
    window.show()
    sys.exit(app.exec())
