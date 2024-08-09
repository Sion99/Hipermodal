import os
import subprocess
import threading
import sys
from PySide6.QtCore import QObject, Signal


class VoiceRecognition(QObject):
    listening_signal = Signal()

    def __init__(self, gesture_controller):
        super().__init__()
        self.gesture_controller = gesture_controller
        self.process = None
        self.thread = None
        self.running = False
        self.CLICK = ['click', 'click.', 'Click', 'Click.', 'Click!', '클릭', '클리', 'Клик.', 'Клик', 'kлик', 'kлик.',
                      'Cleak.', 'Kli', 'Clique.']
        self.DOUBLE_CLICK = ['더블클릭', '더블 클릭', 'Double click.', 'Double click', 'double click', 'Double-click',
                             'double-click']
        self.UP = ['Up', 'Up.', 'up', 'up.', '업', '업.', 'Tom.', 'Oop', 'Oop!', 'Oop.', 'Op!', 'Hopp!', 'Op.', 'Opp.',
                   'Opp', 'Hope.']
        self.DOWN = ['Down', 'Down.', 'down', 'down.', '다운', '다운.', "Don't.", "Don't", 'Town.', 'Ton.', 'Tom', 'Town',
                     'town', 'town.', 'Thone.', "Don't...", '다음', '다은']
        self.IN = ['in', 'in.']
        self.OUT = ['out', 'out.', 'Out', 'Out.']
        self.DRAG = ['Drag.', 'Drag', 'drag.', 'drag', '드래그', '드레그', 'Дройки.', 'Трек.', 'Дрек', '드레', '드래', 'track',
                     'Trek.', 'Hold.', 'Hold', 'hold.', 'hold', 'Holt.', 'old.', 'old', 'holt', 'Ulte.', 'Ulte', 'ulte']
        self.DROP = ['드럽고', '드럽', 'Drop.', 'Drop', 'drop.', 'drop', 'truck.', 'truck', '드라', '드랍', 'Trump', 'trump',
                     '드럼', ]

    def start(self):
        if self.process is None:
            self.running = True
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.process = subprocess.Popen([sys.executable, 'modules/transformer.py'], stdout=subprocess.PIPE,
                                            env=env, text=True)
            self.thread = threading.Thread(target=self.read_output)
            self.thread.start()

    def read_output(self):
        while self.running:
            output = self.process.stdout.readline()
            if output:
                self.handle_result(output.strip())
            else:
                break

    def handle_result(self, result):
        # 음성 인식 결과를 처리하는 코드
        if result in self.CLICK:
            self.gesture_controller.perform_click_action()
        elif result in self.DOUBLE_CLICK:
            self.gesture_controller.perform_double_click_action()
        elif result in self.UP:
            self.gesture_controller.perform_scroll_action('up')
        elif result in self.DOWN:
            self.gesture_controller.perform_scroll_action('down')
        elif result in self.IN:
            self.gesture_controller.perform_zoom_action('in')
        elif result in self.OUT:
            self.gesture_controller.perform_zoom_action('out')
        elif result in self.DRAG:
            self.gesture_controller.perform_drag_action('drag')
        elif result in self.DROP:
            self.gesture_controller.perform_drag_action('drop')
        if result == "Listening...":
            self.listening_signal.emit()

        print(f"음성 인식 모듈: {result}")

    def stop(self):
        self.running = False
        if self.process is not None:
            self.process.terminate()
            self.process = None
        if self.thread is not None:
            self.thread.join()
            self.thread = None
