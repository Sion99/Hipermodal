import cv2
import time


class Webcam:
    def __init__(self, cam_id=0, width=1280, height=720):
        self.cap = cv2.VideoCapture(cam_id)  # CAP_AVFOUNDATION 백엔드를 사용
        self.cap.set(3, width)
        self.cap.set(4, height)
        if not self.cap.isOpened():
            raise Exception("Failed to read the frame. Check the webcam connection.")
        self.previous_time = time.time()

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            print("Failed to read the frame.")
            return None
        return cv2.flip(frame, 1)

    def calculate_fps_and_delay(self):
        current_time = time.time()
        sec = current_time - self.previous_time
        fps = 1 / sec
        self.previous_time = current_time
        return int(fps), int(1000 / fps)

    def release(self):
        self.cap.release()
