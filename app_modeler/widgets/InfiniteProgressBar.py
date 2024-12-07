from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QProgressBar

class InfiniteProgressBar(QProgressBar):
    def __init__(self, control_signal: Signal, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)  # Timer to control the progress
        self.setRange(0, 100)      # Set range to 0-100
        self.timer.timeout.connect(self.update_progress)
        self._progress = 0         # Current progress value
        self._phase = 0            # Current phase of animation

        # Connect the signal to control start and stop
        control_signal.connect(self.handle_signal)

    def handle_signal(self, start: bool):
        """Starts or stops the infinite progress animation based on signal."""
        if start:
            self.start_infinite()
        else:
            self.stop_infinite()

    def start_infinite(self):
        """Starts the infinite progress animation."""
        self._progress = 0
        self._phase = 0
        self.timer.start(50)  # Adjust the interval for desired speed

    def stop_infinite(self):
        """Stops the infinite progress animation."""
        self.timer.stop()
        self.reset()  # Resets the progress bar to 0

    def update_progress(self):
        """Updates the progress bar with dynamic visualization."""
        if self._phase == 0:
            # Normal progress from left to right
            self._progress += 2
            if self._progress > 100:
                self._progress = 0
                self._phase = 1
        elif self._phase == 1:
            # Flowing effect from left to right
            self._progress += 5
            if self._progress > 100:
                self._progress = 0
                self._phase = 0
        self.setValue(self._progress)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

    class MainWindow(QWidget):
        progressing = Signal(bool)

        def __init__(self):
            super().__init__()
            self.setWindowTitle('Progress Widget Example')

            layout = QVBoxLayout(self)

            self.button = QPushButton('Start Process', self)
            self.button.clicked.connect(self.start_process)
            layout.addWidget(self.button)

            # Create the ProgressWidget
            self.progress_widget = InfiniteProgressBar(self.progressing, self)

            # Simulate a process using a QTimer
            self.timer = QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.process_finished)

        def start_process(self):
            self.progress_widget.start_infinite()
            self.timer.start(5000)  # Simulate a process that takes 5 seconds

        def process_finished(self):
            self.progress_widget.stop_infinite()


    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
