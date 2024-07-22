import sys
from PySide6.QtCore import QIODevice, QBuffer
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PySide6.QtMultimedia import QAudioSource, QAudioFormat, QMediaDevices


class AudioRecorder(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        # 오디오 형식 설정
        format = QAudioFormat()
        format.setSampleRate(44100)
        format.setChannelCount(2)
        format.setSampleFormat(QAudioFormat.Int16)

        # 오디오 입력 초기화
        self.audio_source = QAudioSource(QMediaDevices.defaultAudioInput(), format, self)
        self.buffer = QBuffer()
        self.buffer.open(QIODevice.ReadWrite)

    def init_ui(self):
        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 300, 100)

        self.layout = QVBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.setEnabled(False)

        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.setLayout(self.layout)

        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)

    def start_recording(self):
        self.buffer.seek(0)
        self.buffer.buffer().clear()
        self.audio_source.start(self.buffer)

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recording(self):
        self.audio_source.stop()
        self.save_audio()

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def save_audio(self):
        with open("output.wav", "wb") as f:
            f.write(b'RIFF')
            f.write((36 + self.buffer.size()).to_bytes(4, 'little'))
            f.write(b'WAVEfmt ')
            f.write((16).to_bytes(4, 'little'))
            f.write((1).to_bytes(2, 'little'))
            f.write((2).to_bytes(2, 'little'))
            f.write((44100).to_bytes(4, 'little'))
            f.write((44100 * 2 * 2).to_bytes(4, 'little'))
            f.write((2 * 2).to_bytes(2, 'little'))
            f.write((16).to_bytes(2, 'little'))
            f.write(b'data')
            f.write(self.buffer.size().to_bytes(4, 'little'))
            f.write(self.buffer.data())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    recorder = AudioRecorder()
    recorder.show()
    sys.exit(app.exec())
