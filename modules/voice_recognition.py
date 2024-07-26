import subprocess
import threading


class VoiceRecognition:
    def __init__(self):
        self.process = None
        self.thread = None
        self.running = False

    def start(self):
        if self.process is None:
            self.running = True
            self.process = subprocess.Popen(['python', 'modules/transformer.py'], stdout=subprocess.PIPE,
                                            text=True)
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
        print(f"음성 인식 모듈: {result}")

    def stop(self):
        self.running = False
        if self.process is not None:
            self.process.terminate()
            self.process = None
        if self.thread is not None:
            self.thread.join()
            self.thread = None
