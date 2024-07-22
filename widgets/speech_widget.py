from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from modules.voice_thread import VoiceThread


class SpeechWidget(QWidget):
    def __init__(self, parent=None):
        super(SpeechWidget, self).__init__(parent)

        # VoiceThread 초기화
        self.voice_thread = VoiceThread()
        self.voice_thread.start()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Control panel
        self.control_panel = QWidget()
        self.control_layout = QGridLayout()



