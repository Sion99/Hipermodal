import subprocess
from PySide6.QtCore import QThread, Signal
import threading


class VoiceThread(QThread):
    result_signal = Signal(str)

    def __init__(self):
        super(VoiceThread, self).__init__()
        self.process = None
        self.thread = None
        self.running = False

    def run(self):
        self.running = True
        self.process = subprocess.Popen(['python', 'voice_recognition_script.py'], stdout=subprocess.PIPE, text=True)
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
        self.result_signal.emit(result)  # 결과를 시그널로 전달

    def stop(self):
        self.running = False
        if self.process is not None:
            self.process.terminate()
            self.process = None
        if self.thread is not None:
            self.thread.join()
            self.thread = None
        self.quit()
        self.wait(500)
