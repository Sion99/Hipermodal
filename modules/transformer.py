import pyaudio
import torch
import numpy as np
import ssl
from transformers import pipeline


class VoiceCommandController:
    def __init__(self):
        self.running = False
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.transcriber = pipeline(
            "automatic-speech-recognition", model="openai/whisper-base", device=self.device
        )
        self.CHUNK = 4096
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000

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
    voice_controller = VoiceCommandController()
    try:
        voice_controller.run()
    except KeyboardInterrupt:
        print("Voice recognition stopped by user")
        voice_controller.stop()
