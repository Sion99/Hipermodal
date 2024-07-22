import threading

import speech_recognition as sr


class VoiceCommandController:
    def __init__(self):
        self.running = False
        self.timeout = 10
        self.phrase_timeout_limit = 10

    def start_voice_recognition(self):
        self.recognition_active = True

    def stop_voice_recognition(self):
        self.recognition_active = False

    def run(self):
        self.running = True

        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

        process_thread = threading.Thread(target=self.process)
        process_thread.start()



