import ssl
import speech_recognition as sr
import time


class VoiceCommandController:
    def __init__(self, gesture_controller):
        self.gesture_controller = gesture_controller
        self.running = False
        self.timeout = 5
        self.phrase_timeout_limit = 5
        self.recognizer = sr.Recognizer()
        ssl._create_default_https_context = ssl._create_unverified_context
        self.microphone = sr.Microphone()  # 마이크 객체를 초기화하여 재사용

    def run(self):
        self.running = True
        while self.running:
            print('Listening...')
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=self.timeout,
                                                   phrase_time_limit=self.phrase_timeout_limit)
                print('Processing...')
                text = self.recognizer.recognize_whisper(audio, language='ko')
                print(f"Recognized: {text}")
            except sr.UnknownValueError:
                print('Recognizer Failed..')
            except sr.RequestError as e:
                print(f'Request Failed... {e}')
            except Exception as e:
                print(f'An error occurred: {e}')
                time.sleep(1)  # 예외가 발생하면 잠시 대기 후 재시도

    def stop(self):
        self.running = False


# 사용 예시
if __name__ == "__main__":
    from gesture import HandGestureController

    gesture_controller = HandGestureController()
    voice_controller = VoiceCommandController(gesture_controller)

    try:
        voice_controller.run()
    except KeyboardInterrupt:
        print("Voice recognition stopped by user")
        voice_controller.stop()
