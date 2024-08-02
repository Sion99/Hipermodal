import sys
from PySide6.QtGui import QAction, QCursor, QPainter, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QCheckBox, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QGridLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint
from widgets.video_widget import VideoWidget


class IndicatorLabel(QLabel):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(15, 15)  # 원의 크기 조절

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(self.color))
        painter.setPen(QColor(self.color))
        painter.drawEllipse(0, 0, self.width(), self.height())


class Switch(QCheckBox):
    def __init__(self, parent=None):
        super(Switch, self).__init__(parent)
        self.setFixedSize(60, 30)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet('''
            QCheckBox {
                background-color: #ccc;
                border-radius: 15px;
                border: 2px solid #ccc;
                width: 60px;
                height: 30px;
                padding: 0;
                margin: 0;
            }
            QCheckBox::indicator {
                width: 26px;
                height: 26px;
                border-radius: 13px;
                background-color: white;
                position: absolute;
                left: 1px;
                top: 1px;
            }
            QCheckBox::indicator:checked {
                left: 32px;
            }
            QCheckBox:checked {
                background-color: #66bb6a;
                border: 2px solid #66bb6a;
            }
        ''')

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.stateChanged.connect(self.start_animation)

    def start_animation(self, state):
        if state == Qt.Checked:
            self.animation.setEndValue(self.mapToParent(self.rect().topLeft() + QPoint(32, 0)))
        else:
            self.animation.setEndValue(self.mapToParent(self.rect().topLeft() + QPoint(1, 0)))
        self.animation.start()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setFixedSize(690, 800)
        self.setWindowTitle("Hiperwall Multimodal")

        # Status Bar
        self.statusBar().showMessage('프로그램 실행 완료', 3000)
        self.video_widget = VideoWidget()

        self.menuBar().setNativeMenuBar(False)  # macOS 에서만
        filemenu = self.menuBar().addMenu("&File")

        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+W')
        exitAction.setStatusTip('프로그램 종료')
        exitAction.triggered.connect(QApplication.quit)
        filemenu.addAction(exitAction)

        # 레이아웃을 위한 위젯 생성
        layout_widget = QWidget()
        layout = QHBoxLayout(layout_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # 카메라, 마이크 인디케이터 설정
        self.camera_indicator = IndicatorLabel('green')
        self.camera_indicator.setToolTip('카메라로 제스처를 감지중입니다.')
        self.mic_indicator = IndicatorLabel('orange')
        self.mic_indicator.setToolTip('마이크로 음성을 감지중입니다.')

        # 레이아웃에 인디케이터 추가
        layout.addWidget(self.camera_indicator)
        layout.addWidget(self.mic_indicator)

        # 상태 표시줄에 레이아웃 위젯 추가
        self.statusBar().addPermanentWidget(layout_widget)

        # 기본적으로 인디케이터 숨김
        self.camera_indicator.hide()
        self.mic_indicator.hide()

        # QLabel 스타일 설정
        label_style = """
        QLabel {
            font-size: 18px;  /* 글씨 크기 설정 */
            color: #333;      /* 글씨 색상 설정 */
        }
        """

        # 제스처 모드 스위치와 라벨
        self.toggle_layout = QGridLayout()
        self.gesture_label = QLabel("     제스처 모드")
        self.gesture_label.setStyleSheet(label_style)
        self.gesture_toggle_switch = Switch()
        self.gesture_toggle_switch.stateChanged.connect(self.toggle_gesture_mode)
        self.toggle_layout.addWidget(self.gesture_label, 4, 1)
        self.toggle_layout.addWidget(self.gesture_toggle_switch, 4, 2)

        self.speech_label = QLabel("       음성 인식")
        self.speech_label.setStyleSheet(label_style)
        self.speech_toggle_switch = Switch()
        self.speech_toggle_switch.setEnabled(False)
        self.speech_toggle_switch.stateChanged.connect(self.toggle_speech_mode)
        self.toggle_layout.addWidget(self.speech_label, 4, 4)
        self.toggle_layout.addWidget(self.speech_toggle_switch, 4, 5)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_widget)
        self.layout.addLayout(self.toggle_layout)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # 배경 색상 설정
        self.setStyleSheet("background-color: #ffffff;")  # 여기에 원하는 색상을 입력하세요.

        # 제스처 모드 단축키
        self.gesture_shortcut = QAction('Toggle Gesture Mode', self)
        self.gesture_shortcut.setShortcut('Ctrl+C')
        self.gesture_shortcut.setStatusTip('Toggle Gesture Mode')
        self.gesture_shortcut.triggered.connect(self.toggle_gesture_mode_shortcut)
        self.addAction(self.gesture_shortcut)
        filemenu.addAction(self.gesture_shortcut)

        # 음성 인식 단축키
        self.speech_shortcut = QAction('Toggle Speech Mode', self)
        self.speech_shortcut.setShortcut('Ctrl+V')
        self.speech_shortcut.setStatusTip('Toggle Speech Mode')
        self.speech_shortcut.triggered.connect(self.toggle_speech_mode_shortcut)
        self.addAction(self.speech_shortcut)
        filemenu.addAction(self.speech_shortcut)

    def toggle_gesture_mode(self, state):
        if self.gesture_toggle_switch.isChecked():
            self.video_widget.gesture_thread.start_gesture_recognition()
            self.speech_toggle_switch.setEnabled(True)
            self.statusBar().showMessage('제스처 모드가 활성화되었습니다.', 3000)
            self.camera_indicator.setVisible(True)
        else:
            self.video_widget.gesture_thread.stop_gesture_recognition()
            self.video_widget.voice_recognition_stop()
            self.speech_toggle_switch.setEnabled(False)
            self.speech_toggle_switch.setChecked(False)
            self.statusBar().showMessage('제스처 모드가 비활성화되었습니다.', 3000)
            self.camera_indicator.setVisible(False)
            self.mic_indicator.setVisible(False)

    def toggle_speech_mode(self, state):
        if self.speech_toggle_switch.isChecked():
            self.video_widget.voice_recognition_start()
            self.mic_indicator.setVisible(True)
            self.statusBar().showMessage('음성 인식이 활성화되었습니다.', 3000)
        else:
            self.video_widget.voice_recognition_stop()
            self.mic_indicator.setVisible(False)
            self.statusBar().showMessage('음성 인식이 비활성화되었습니다.', 3000)

    def toggle_gesture_mode_shortcut(self):
        self.gesture_toggle_switch.setChecked(not self.gesture_toggle_switch.isChecked())

    def toggle_speech_mode_shortcut(self):
        if self.speech_toggle_switch.isEnabled():
            self.speech_toggle_switch.setChecked(not self.speech_toggle_switch.isChecked())

    def closeEvent(self, event):
        self.statusBar().showMessage('프로그램 종료 중... 잠시만 기다려주세요.')
        self.video_widget.closeEvent(event)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())