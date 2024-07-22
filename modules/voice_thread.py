from PySide6.QtCore import QThread
from modules.voice import VoiceCommandController


class VoiceThread(QThread):
    def __init__(self):
        super(VoiceThread, self).__init__()
        self.voice_command_controller = VoiceCommandController()
        self._running = False

    def run(self):
        self._running = True
        self.hand_gesture_controller.run()

    def start_voice_recognition(self):
        self.voice_command_controller.start_voice_recognition()

    def stop_voice_recognition(self):
        self.voice_command_controller.stop_voice_recognition()

    def stop(self):
        self._running = False
        self.quit()
        self.wait(500)
        self.voice_command_controller.stop()
