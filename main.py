import sys
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from widgets.video_widget import VideoWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setFixedSize(690, 800)
        self.setWindowTitle("Hiperwall Multimodal")

        # Status Bar
        self.statusBar().showMessage('프로그램 실행 완료', 3000)


        self.menuBar().setNativeMenuBar(False)  # macOS 에서만
        filemenu = self.menuBar().addMenu("&File")

        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+W')
        exitAction.setStatusTip('프로그램 종료')
        exitAction.triggered.connect(QApplication.quit)
        filemenu.addAction(exitAction)

        self.video_widget = VideoWidget()

        self.gesture_toggle_button = QPushButton("제스처 모드 활성화")
        self.gesture_toggle_button.setCheckable(True)
        self.gesture_toggle_button.clicked.connect(self.toggle_gesture_mode)

        self.speech_toggle_button = QPushButton("음성 인식 활성화")
        self.speech_toggle_button.setCheckable(True)
        # self.speech_toggle_button.clicked.connect(self.toggle_speech_mode)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_widget)
        self.layout.addWidget(self.gesture_toggle_button)
        self.layout.addWidget(self.speech_toggle_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

    def toggle_gesture_mode(self):
        if self.gesture_toggle_button.isChecked():
            self.video_widget.gesture_thread.start_gesture_recognition()
            self.statusBar().showMessage('제스처 모드 ON', 3000)
        else:
            self.video_widget.gesture_thread.stop_gesture_recognition()
            self.statusBar().showMessage('제스처 모드 OFF', 3000)

    # def toggle_speech_mode(self):
    #     if self.speech_toggle_button.isChecked():
    #         self.video_widget.speech_recognition.start_recognition()
    #     else:
    #         self.video_widget.speech_recognition.stop_recognition()

    def closeEvent(self, event):
        self.statusBar().showMessage('프로그램 종료 중... 잠시만 기다려주세요.')
        self.video_widget.closeEvent(event)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())