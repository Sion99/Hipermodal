import threading
from PySide6.QtCore import QObject, Signal
import multiprocessing
import pyaudio
import torch
import numpy as np
import ssl
from transformers import pipeline

# Windows에서의 프로세스 생성 문제를 방지하기 위해 freeze_support 호출
multiprocessing.freeze_support()


def transformer_process(queue):
    """음성 인식 및 결과를 처리하는 별도 프로세스."""
    ssl._create_default_https_context = ssl._create_unverified_context
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    transcriber = pipeline(
        "automatic-speech-recognition", model="openai/whisper-base", device=device
    )
    CHUNK = 4096
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()

    # 스트림 열기
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Listening...")
    queue.put("Listening...")

    frames = []

    try:
        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(np.frombuffer(data, np.int16))
            except IOError as e:
                print(f"Input overflowed: {e}")
                continue

            # 매 2초마다 데이터를 처리
            if len(frames) * CHUNK >= RATE:
                audio_input = np.concatenate(frames)
                audio_input = audio_input.astype(np.float32) / np.max(np.abs(audio_input))
                frames = []

                # 모델로 텍스트 변환 및 유니코드 에러 처리 (Windows 에러)
                try:
                    text = transcriber({"sampling_rate": RATE, "raw": audio_input})["text"].strip()
                    queue.put(text)
                except UnicodeEncodeError as e:
                    print("유니코드 깨짐")
                    continue

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        if stream.is_active():
            stream.stop_stream()
        stream.close()
        p.terminate()


class VoiceRecognition(QObject):
    listening_signal = Signal()

    def __init__(self, gesture_controller):
        super().__init__()
        self.gesture_controller = gesture_controller
        self.result_queue = multiprocessing.Queue()
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
            self.process = multiprocessing.Process(target=transformer_process, args=(self.result_queue,))
            self.process.start()
            self.thread = threading.Thread(target=self.read_output)
            self.thread.start()

    def read_output(self):
        while self.running:
            if not self.result_queue.empty():
                result = self.result_queue.get()
                self.handle_result(result)

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
            self.process.join()
            self.process = None
        if self.thread is not None:
            self.thread.join()
            self.thread = None
