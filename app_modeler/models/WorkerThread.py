import logging

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)

class WorkerThread(QThread):
    """
    WorkerThread is a QThread subclass that runs an arbitrary function with provided arguments.
    """
    # Define signals to emit results, errors, and completion status
    result_signal = Signal(object)
    error_signal = Signal(Exception)
    finished_signal = Signal()
    busy = Signal(bool)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # Execute the function with arguments
            self.busy.emit(True)
            result = self.function(*self.args, **self.kwargs)
            # Emit the result
            self.result_signal.emit(result)
        except Exception as error:
            # Emit any exceptions as strings
            logger.warning(f"Error in WorkerThread: {error}", stack_info=True, stacklevel=10, exc_info=True)
            self.error_signal.emit(error)
        finally:
            # Emit a finished signal
            self.finished_signal.emit()
            self.busy.emit(False)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    def example_function(a, b):
        return a + b
    app = QApplication([])
    worker = WorkerThread(example_function, 1, 2)
    worker.result_signal.connect(print)
    worker.error_signal.connect(print)
    worker.finished_signal.connect(lambda: print("Finished"))
    worker.start()
    worker.wait(20)
    app.exec()

