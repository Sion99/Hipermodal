import cv2
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollBar, QHBoxLayout, QGridLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt
from modules.gesture_thread import GestureThread


class VideoWidget(QWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)

        # GestureThread 초기화
        self.gesture_thread = GestureThread()
        self.gesture_thread.start()

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Video display
        self.video_label = QLabel()
        self.layout.addWidget(self.video_label)

        # Control panel
        self.control_panel = QWidget()
        self.control_layout = QGridLayout()

        # Mouse Sensitivity
        self.mouse_sensitivity_label = QLabel("Mouse Sensitivity")
        self.mouse_sensitivity_slider = QScrollBar(Qt.Horizontal)
        self.mouse_sensitivity_slider.setMinimum(1)
        self.mouse_sensitivity_slider.setMaximum(100)
        self.mouse_sensitivity_slider.setValue(
            self.scale_mouse_sensitivity(self.gesture_thread.hand_gesture_controller.mouse_sensitivity))
        self.mouse_sensitivity_slider.valueChanged.connect(self.update_mouse_sensitivity)
        self.mouse_sensitivity_value_label = QLabel(
            f"{self.gesture_thread.hand_gesture_controller.mouse_sensitivity:.1f}")

        mouse_sensitivity_layout = QHBoxLayout()
        mouse_sensitivity_layout.addWidget(self.mouse_sensitivity_slider)
        mouse_sensitivity_layout.addWidget(self.mouse_sensitivity_value_label)

        # Scroll Sensitivity
        self.scroll_sensitivity_label = QLabel("Scroll Sensitivity")
        self.scroll_sensitivity_slider = QScrollBar(Qt.Horizontal)
        self.scroll_sensitivity_slider.setMinimum(1)
        self.scroll_sensitivity_slider.setMaximum(100)
        self.scroll_sensitivity_slider.setValue(
            self.scale_scroll_sensitivity(self.gesture_thread.hand_gesture_controller.scroll_sensitivity))
        self.scroll_sensitivity_slider.valueChanged.connect(self.update_scroll_sensitivity)
        self.scroll_sensitivity_value_label = QLabel(
            f"{self.gesture_thread.hand_gesture_controller.scroll_sensitivity:.1f}")

        scroll_sensitivity_layout = QHBoxLayout()
        scroll_sensitivity_layout.addWidget(self.scroll_sensitivity_slider)
        scroll_sensitivity_layout.addWidget(self.scroll_sensitivity_value_label)

        # Adding to control layout
        self.control_layout.addWidget(self.mouse_sensitivity_label, 0, 0)
        self.control_layout.addLayout(mouse_sensitivity_layout, 0, 1)
        self.control_layout.addWidget(self.scroll_sensitivity_label, 1, 0)
        self.control_layout.addLayout(scroll_sensitivity_layout, 1, 1)

        # Status labels
        self.fps_label = QLabel("FPS: 0")
        self.delay_label = QLabel("DELAY: 0 ms")
        self.last_action_label = QLabel("Last Action: None")

        self.control_layout.addWidget(self.fps_label, 2, 0)
        self.control_layout.addWidget(self.delay_label, 2, 1)
        self.control_layout.addWidget(self.last_action_label, 3, 0, 1, 2)

        self.control_panel.setLayout(self.control_layout)
        self.layout.addWidget(self.control_panel)

        self.setLayout(self.layout)

    def scale_mouse_sensitivity(self, sensitivity):
        return int((sensitivity - 0.1) * 100 / 2.8)

    def scale_scroll_sensitivity(self, sensitivity):
        return int((sensitivity - 0.1) * 100 / 1.4)

    def inverse_scale_mouse_sensitivity(self, value):
        return 0.1 + value * 2.8 / 100

    def inverse_scale_scroll_sensitivity(self, value):
        return 0.1 + value * 1.4 / 100

    def update_mouse_sensitivity(self, value):
        sensitivity = self.inverse_scale_mouse_sensitivity(value)
        self.gesture_thread.hand_gesture_controller.mouse_sensitivity = sensitivity
        self.mouse_sensitivity_value_label.setText(f"{sensitivity:.1f}")

    def update_scroll_sensitivity(self, value):
        sensitivity = self.inverse_scale_scroll_sensitivity(value)
        self.gesture_thread.hand_gesture_controller.scroll_sensitivity = sensitivity
        self.scroll_sensitivity_value_label.setText(f"{sensitivity:.1f}")

    def update_frame(self):
        try:
            frame = self.gesture_thread.hand_gesture_controller.get_frame()
            if frame is None:
                print("No frame captured")
                return

            # OpenCV to QImage conversion
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            step = channel * width
            q_img = QImage(image.data, width, height, step, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))

            # Update status labels
            fps, delay = self.gesture_thread.hand_gesture_controller.cap.calculate_fps_and_delay()
            self.fps_label.setText(f"FPS: {fps}")
            self.delay_label.setText(f"DELAY: {delay} ms")
            self.last_action_label.setText(f"Last Action: {self.gesture_thread.hand_gesture_controller.last_gesture}")
        except Exception as e:
            print(f"Error in update_frame: {e}")

    def closeEvent(self, event):
        self.gesture_thread.stop()
        self.gesture_thread.wait()
        self.speech_recognition.stop_recognition()
        event.accept()
