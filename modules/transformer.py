import pyaudio
import torch
import numpy as np
import ssl
from transformers import pipeline


class VoiceCommandController:
    def __init__(self):
        # self.gesture_controller = gesture_controller
        self.running = False
        # ssl._create_default_https_context = ssl._create_unverified_context
        self.transcriber = pipeline(
            "automatic-speech-recognition", model="openai/whisper-base"
        )
        self.CHUNK = 4096
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CLICK = ['click', 'click.', 'Click', 'Click.', 'Click!', '클릭', '클리', 'Клик.', 'Клик', 'kлик', 'kлик.', 'Cleak.', 'Kli', 'Clique.']
        self.DOUBLE_CLICK = ['더블클릭', '더블 클릭', 'Double click.', 'Double click', 'double click', 'Double-click', 'double-click']
        self.UP = ['Up', 'Up.', 'up', 'up.', '업', '업.', 'Tom.', 'Oop', 'Oop!', 'Oop.', 'Op!', 'Hopp!', 'Op.', 'Opp.', 'Opp', 'Oh', 'Oh.', 'Hope.']
        self.DOWN = ['Down', 'Down.', 'down', 'down.', '다운', '다운.', "Don't.", "Don't", 'Town.', 'Ton.', 'Tom', 'Town', 'town', 'town.', 'Thone.', "Don't...", '다음', '다은']
        self.IN = ['in', 'in.']
        self.OUT = ['out', 'out.', 'Out', 'Out.']
        self.DRAG = ['Drag.', 'Drag', 'drag.', 'drag', '드래그', '드레그', 'Дройки.', 'Трек.', 'Дрек', '드레', '드래', 'track', 'Trek.', 'Hold.', 'Hold', 'hold.', 'hold', 'Holt.', 'old.', 'old', 'holt', 'Ulte.', 'Ulte', 'ulte']
        self.DROP = ['드럽고', '드럽', 'Drop.', 'Drop', 'drop.', 'drop', 'truck.', 'truck', '드라', '드랍', 'Trump', 'trump', '드럼', ]

    def run(self):
        self.running = True
        p = pyaudio.PyAudio()

        # 스트림 열기
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)

        print("Listening...")

        frames = []

        try:
            while True:
                try:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    frames.append(np.frombuffer(data, np.int16))
                except IOError as e:
                    print(f"Input overflowed: {e}")
                    continue

                # 매 2초마다 데이터를 처리 (기존보다 더 길게 처리)
                if len(frames) * self.CHUNK >= self.RATE:
                    audio_input = np.concatenate(frames)
                    audio_input = audio_input.astype(np.float32) / np.max(np.abs(audio_input))  # 정규화
                    frames = []

                    # 모델로 텍스트 변환 및 유니코드 에러 처리 (Windows 에러)
                    try:
                        text = self.transcriber({"sampling_rate": self.RATE, "raw": audio_input})["text"].strip()
                        print(text)
                    except UnicodeEncodeError as e:
                        print("유니코드 깨짐")
                        continue

                    # if text in self.CLICK:
                    #     gesture_controller.perform_click_action()
                    # elif text in self.DOUBLE_CLICK:
                    #     gesture_controller.perform_double_click_action()
                    # elif text in self.UP:
                    #     gesture_controller.perform_scroll_action('up')
                    # elif text in self.DOWN:
                    #     gesture_controller.perform_scroll_action('down')
                    # elif text in self.IN:
                    #     gesture_controller.perform_zoom_action('in')
                    # elif text in self.OUT:
                    #     gesture_controller.perform_zoom_action('out')
                    # elif text in self.DRAG:
                    #     gesture_controller.perform_drag_action('drag')
                    # elif text in self.DROP:
                    #     gesture_controller.perform_drag_action('drop')

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            if stream.is_active():
                stream.stop_stream()
            stream.close()
            p.terminate()

    def stop(self):
        self.running = False


if __name__ == "__main__":
    # from gesture import HandGestureController
    #
    # gesture_controller = HandGestureController()
    voice_controller = VoiceCommandController()

    try:
        voice_controller.run()
    except KeyboardInterrupt:
        print("Voice recognition stopped by user")
        voice_controller.stop()
