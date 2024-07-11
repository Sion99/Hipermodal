from PySide6.QtCore import QThread
from modules.gesture import HandGestureController


class GestureThread(QThread):
    def __init__(self):
        super(GestureThread, self).__init__()
        self.hand_gesture_controller = HandGestureController()
        self._running = False

    def run(self):
        self._running = True
        self.hand_gesture_controller.run()

    def start_gesture_recognition(self):
        self.hand_gesture_controller.start_gesture_recognition()

    def stop_gesture_recognition(self):
        self.hand_gesture_controller.stop_gesture_recognition()

    def stop(self):
        self._running = False
        self.quit()
        self.wait(500)
        self.hand_gesture_controller.stop()
