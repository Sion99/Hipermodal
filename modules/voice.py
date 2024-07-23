import threading
import ssl
import speech_recognition as sr
import time


class VoiceCommandController:
    def __init__(self):
        self.running = False
        self.recognition_active = False
        self.timeout = 10
        self.phrase_timeout_limit = 10
        self.last_gesture = None
        self.listen_thread = None
        self.recognizer = sr.Recognizer()
        self.lock = threading.Lock()
        ssl._create_default_https_context = ssl._create_unverified_context

    def start_voice_recognition(self):
        with self.lock:
            self.recognition_active = True

    def stop_voice_recognition(self):
        with self.lock:
            self.recognition_active = False

    def run(self):
        self.running = True
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

    def listen(self):
        with sr.Microphone() as source:
            while self.running:
                with self.lock:
                    if not self.recognition_active:
                        time.sleep(0.1)
                        continue
                print('음성을 듣는 중...')
                try:
                    audio = self.recognizer.listen(source, timeout=self.timeout,
                                                   phrase_time_limit=self.phrase_timeout_limit)
                    print('처리 중...')
                    text = self.recognizer.recognize_whisper(audio, language='ko')
                    print(f"감지한 음성: {text}")
                except sr.UnknownValueError:
                    print('Recognizer Failed..')
                except sr.RequestError as e:
                    print(f'Request Failed... {e}')
                except Exception as e:
                    print(f'An error occurred: {e}')

    def stop(self):
        self.running = False
        if self.listen_thread is not None:
            self.listen_thread.join()
            self.listen_thread = None


# 사용 예시
if __name__ == "__main__":
    controller = VoiceCommandController()
    controller.run()
    time.sleep(5)  # 음성 인식 테스트 시간을 줍니다.
    controller.start_voice_recognition()
    time.sleep(20)  # 음성 인식 활성화 시간을 줍니다.
    controller.stop_voice_recognition()
    controller.stop()
