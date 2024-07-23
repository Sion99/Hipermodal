import sys
import cv2
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollBar, QHBoxLayout, QGridLayout, QErrorMessage
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt
from modules.gesture_thread import GestureThread
from modules.voice_recognition import VoiceRecognition


class VideoWidget(QWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)

        # GestureThread 초기화
        self.gesture_thread = GestureThread()
        self.gesture_thread.start()

        self.voice_recognition = VoiceRecognition()

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.no_frame_count = 0
        self.timer.start(30)

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Video display
        self.video_label = QLabel()
        self.layout.addWidget(self.video_label)

        # Control panel
        self.control_panel = QWidget()
        self.control_layout = QGridLayout()

        label_style = """
        QLabel {
            font-size: 14px;
            color: #333;
        }
        """

        scrollbar_style = """
        QScrollBar:horizontal {
            border: 1px solid #999999;
            background: #f0f0f0;
            height: 12px;
            margin: 0px 20px 0 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #b0b0b0;
            min-width: 20px;
            border-radius: 6px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
            width: 20px;
            subcontrol-origin: margin;
        }
        QScrollBar::add-line:horizontal:hover, QScrollBar::sub-line:horizontal:hover {
            background: #d0d0d0;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
        """

        # Mouse Sensitivity
        self.mouse_sensitivity_label = QLabel("Mouse Sensitivity")
        self.mouse_sensitivity_label.setToolTip('마우스 포인터 감도를 조절합니다.')
        self.mouse_sensitivity_label.setStyleSheet(label_style)
        self.mouse_sensitivity_slider = QScrollBar(Qt.Horizontal)
        self.mouse_sensitivity_slider.setMinimum(1)
        self.mouse_sensitivity_slider.setMaximum(100)
        self.mouse_sensitivity_slider.setValue(
            self.scale_mouse_sensitivity(self.gesture_thread.hand_gesture_controller.mouse_sensitivity))
        self.mouse_sensitivity_slider.valueChanged.connect(self.update_mouse_sensitivity)
        self.mouse_sensitivity_slider.setStyleSheet(scrollbar_style)
        self.mouse_sensitivity_value_label = QLabel(
            f"{self.gesture_thread.hand_gesture_controller.mouse_sensitivity:.1f}")
        self.mouse_sensitivity_value_label.setStyleSheet(label_style)

        mouse_sensitivity_layout = QHBoxLayout()
        mouse_sensitivity_layout.addWidget(self.mouse_sensitivity_slider)
        mouse_sensitivity_layout.addWidget(self.mouse_sensitivity_value_label)

        # Scroll Sensitivity
        self.scroll_sensitivity_label = QLabel("Scroll Sensitivity")
        self.scroll_sensitivity_label.setToolTip('스크롤 감도를 조절합니다.')
        self.scroll_sensitivity_label.setStyleSheet(label_style)
        self.scroll_sensitivity_slider = QScrollBar(Qt.Horizontal)
        self.scroll_sensitivity_slider.setMinimum(1)
        self.scroll_sensitivity_slider.setMaximum(100)
        self.scroll_sensitivity_slider.setValue(
            self.scale_scroll_sensitivity(self.gesture_thread.hand_gesture_controller.scroll_sensitivity))
        self.scroll_sensitivity_slider.valueChanged.connect(self.update_scroll_sensitivity)
        self.scroll_sensitivity_slider.setStyleSheet(scrollbar_style)
        self.scroll_sensitivity_value_label = QLabel(
            f"{self.gesture_thread.hand_gesture_controller.scroll_sensitivity:.1f}")
        self.scroll_sensitivity_value_label.setStyleSheet(label_style)

        scroll_sensitivity_layout = QHBoxLayout()
        scroll_sensitivity_layout.addWidget(self.scroll_sensitivity_slider)
        scroll_sensitivity_layout.addWidget(self.scroll_sensitivity_value_label)

        # Poll Rate
        self.poll_rate_label = QLabel("Polling Rate")
        self.poll_rate_label.setToolTip('마우스 반응속도를 조절합니다.')
        self.poll_rate_label.setStyleSheet(label_style)
        self.poll_rate_slider = QScrollBar(Qt.Horizontal)
        self.poll_rate_slider.setMinimum(1)
        self.poll_rate_slider.setMaximum(100)
        self.poll_rate_slider.setValue(self.scale_poll_rate(self.gesture_thread.hand_gesture_controller.poll_rate))
        self.poll_rate_slider.valueChanged.connect(self.update_poll_rate)
        self.poll_rate_slider.setStyleSheet(scrollbar_style)
        self.poll_rate_value_label = QLabel(f"{self.gesture_thread.hand_gesture_controller.poll_rate:.3f} s")
        self.poll_rate_value_label.setStyleSheet(label_style)

        poll_rate_layout = QHBoxLayout()
        poll_rate_layout.addWidget(self.poll_rate_slider)
        poll_rate_layout.addWidget(self.poll_rate_value_label)

        # Adding to control layout
        self.control_layout.addWidget(self.mouse_sensitivity_label, 0, 0)
        self.control_layout.addLayout(mouse_sensitivity_layout, 0, 1)
        self.control_layout.addWidget(self.scroll_sensitivity_label, 1, 0)
        self.control_layout.addLayout(scroll_sensitivity_layout, 1, 1)
        self.control_layout.addWidget(self.poll_rate_label, 2, 0)
        self.control_layout.addLayout(poll_rate_layout, 2, 1)

        # Status labels
        self.last_action_label = QLabel("현재 제스처: None")
        self.last_action_label.setStyleSheet(label_style)

        self.control_layout.addWidget(self.last_action_label, 4, 0, 1, 2)

        self.control_panel.setLayout(self.control_layout)
        self.layout.addWidget(self.control_panel)

        self.setLayout(self.layout)

    def scale_mouse_sensitivity(self, sensitivity):
        return int((sensitivity - 0.1) * 100 / 2.8)

    def scale_scroll_sensitivity(self, sensitivity):
        return int((sensitivity - 0.1) * 100 / 1.4)

    def scale_poll_rate(self, poll_rate):
        return int((poll_rate - 0.001) * 100 / 0.009)

    def inverse_scale_mouse_sensitivity(self, value):
        return 0.1 + value * 2.8 / 100

    def inverse_scale_scroll_sensitivity(self, value):
        return 0.1 + value * 1.4 / 100

    def inverse_scale_poll_rate(self, value):
        return 0.001 + value * 0.009 / 100

    def update_mouse_sensitivity(self, value):
        sensitivity = self.inverse_scale_mouse_sensitivity(value)
        self.gesture_thread.hand_gesture_controller.mouse_sensitivity = sensitivity
        self.mouse_sensitivity_value_label.setText(f"{sensitivity:.1f}")

    def update_scroll_sensitivity(self, value):
        sensitivity = self.inverse_scale_scroll_sensitivity(value)
        self.gesture_thread.hand_gesture_controller.scroll_sensitivity = sensitivity
        self.scroll_sensitivity_value_label.setText(f"{sensitivity:.1f}")

    def update_poll_rate(self, value):
        poll_rate = self.inverse_scale_poll_rate(value)
        self.gesture_thread.hand_gesture_controller.set_poll_rate(poll_rate)
        self.poll_rate_value_label.setText(f"{poll_rate:.3f} s")

    def update_frame(self):
        try:
            frame = self.gesture_thread.hand_gesture_controller.get_frame()
            if frame is None:
                if self.no_frame_count == 30:
                    error_dialog = QErrorMessage()
                    error_dialog.showMessage('카메라 연결상태를 확인하세요.')
                elif self.no_frame_count < 30:
                    print("No frame captured")
                    self.no_frame_count += 1
                return

            # OpenCV to QImage conversion
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            step = channel * width
            q_img = QImage(image.data, width, height, step, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))

            # Update status labels
            self.last_action_label.setText(f"현재 제스처: {self.gesture_thread.hand_gesture_controller.last_gesture}")
        except Exception as e:
            print(f"Error in update_frame: {e}")

    def closeEvent(self, event):
        self.gesture_thread.stop()
        self.gesture_thread.wait()
        self.voice_recognition.stop()
        event.accept()
