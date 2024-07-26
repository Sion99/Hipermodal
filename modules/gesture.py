import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
from collections import deque, Counter
import threading
from screeninfo import get_monitors
from modules.webcam import Webcam


class HandGestureController:
    def __init__(self, buffer_size=10, click_interval=0.6, mouse_sensitivity=0.5, scroll_sensitivity=0.8,
                 poll_rate=0.08):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        self.gesture_buffer = deque(maxlen=buffer_size)
        self.scroll_mode = False
        self.zoom_mode = False
        self.initial_distance = None
        self.last_click_time = time.time()
        self.last_gesture = None
        self.dragging = False
        self.click_interval = click_interval
        self.prev_finger_pos = None
        self.standby_finger_pos = None
        self.frame_queue = deque(maxlen=60)
        self.frame = None
        self.mouse_sensitivity = mouse_sensitivity
        self.scroll_sensitivity = scroll_sensitivity
        self.poll_rate = poll_rate
        self.thumb_index_distance = 1
        self.last_scroll_value = 0

        pyautogui.FAILSAFE = False
        monitors = get_monitors()
        self.total_screen_width = sum(monitor.width for monitor in monitors)
        self.total_screen_height = max(monitor.height for monitor in monitors)
        self.total_screen_width = 1512
        self.total_screen_height = 982
        print(self.total_screen_width, 'x', self.total_screen_height)

        self.cap = Webcam()
        self.recognition_active = False
        self.running = False
        self.frame_lock = threading.Lock()  # Lock for frame synchronization
        self.speech_recognition = False

    def calculate_distance(self, point1, point2):
        return np.linalg.norm(np.array(point1) - np.array(point2))

    def get_finger_status(self, hand_landmarks):
        fingers = []
        if hand_landmarks.landmark[5].x < hand_landmarks.landmark[17].x:  # 왼손
            fingers.append(1 if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x else 0)
        else:  # 오른손
            fingers.append(1 if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x else 0)

        tips = [8, 12, 16, 20]
        pip_joints = [6, 10, 14, 18]
        for tip, pip in zip(tips, pip_joints):
            fingers.append(1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y else 0)

        thumb_tip = (hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y)
        index_tip = (hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y)
        self.thumb_index_distance = self.calculate_distance(thumb_tip, index_tip)
        self.scroll_mode = self.thumb_index_distance < 0.03
        return fingers

    def recognize_gesture(self, fingers_status):
        if not self.speech_recognition:
            if fingers_status == [0, 1, 0, 0, 0]:
                return 'move'
            elif fingers_status == [1, 1, 0, 0, 0]:
                return 'standby'
            elif fingers_status == [1, 0, 0, 0, 0]:
                return 'click'
            elif fingers_status == [1, 1, 1, 0, 0]:
                return 'drag'
            elif fingers_status == [1, 1, 1, 1, 1]:
                return 'move'
            elif self.scroll_mode:
                return 'scroll'
            return 'unknown'
        else:
            if fingers_status == [0, 1, 0, 0, 0]:
                return 'move'
            elif fingers_status == [1, 1, 0, 0, 0]:
                return 'standby'
            elif fingers_status == [1, 1, 1, 1, 1]:
                return 'move'
            return 'unknown'

    def perform_mouse_action(self, gesture, lmList):
        x, y = lmList[8].x, lmList[8].y
        mouse_x, mouse_y = pyautogui.position()

        if self.prev_finger_pos is not None:
            if self.last_gesture == 'standby':
                # Adjust the initial position based on the current finger position
                self.prev_finger_pos = self.standby_finger_pos

            dx = (x - self.prev_finger_pos[0]) * self.total_screen_width * self.mouse_sensitivity
            dy = (y - self.prev_finger_pos[1]) * self.total_screen_height * self.mouse_sensitivity

            dx = max(min(dx, self.total_screen_width - mouse_x), -mouse_x)
            dy = max(min(dy, self.total_screen_height - mouse_y), -mouse_y)

            if gesture == 'move' or self.dragging:
                pyautogui.moveRel(dx, dy)
            elif gesture == 'drag':
                if not self.dragging:
                    pyautogui.mouseDown()
                    self.dragging = True
                pyautogui.moveRel(dx, dy)
            elif gesture == 'scroll':
                dy = int(-dy * self.scroll_sensitivity)
                smoothed_dy = (dy + self.last_scroll_value) / 2
                pyautogui.scroll(smoothed_dy)
                self.last_scroll_value = dy
            elif self.dragging:
                pyautogui.mouseUp()
                self.dragging = False

        self.prev_finger_pos = (x, y)
        self.last_gesture = gesture

    def perform_click_action(self):
        with self.frame_lock:
            current_time = time.time()
            if not self.speech_recognition:  # 제스처 모드일 때
                if current_time - self.last_click_time > self.click_interval:
                    print(f"Performing click: {current_time - self.last_click_time} > {self.click_interval}")
                    pyautogui.click()
                    self.last_click_time = current_time
                    self.last_gesture = 'click'
            else:  # 음성 인식 모드일 때
                if current_time - self.last_click_time > self.click_interval:
                    print(f"Performing click: {current_time - self.last_click_time} > {self.click_interval}")
                    pyautogui.click()
                    self.last_click_time = current_time
                    self.last_gesture = 'click'
                else:
                    print(f"Click not performed: {current_time - self.last_click_time} > {self.click_interval}")

    def perform_double_click_action(self):
        with self.frame_lock:
            current_time = time.time()
            if not self.speech_recognition:  # 제스처 모드일 때
                if current_time - self.last_click_time > self.click_interval:
                    print(f"Performing double click: {current_time - self.last_click_time} > {self.click_interval}")
                    pyautogui.doubleClick()
                    self.last_click_time = current_time
                    self.last_gesture = 'double click'
            else:  # 음성 인식 모드일 때
                if current_time - self.last_click_time > self.click_interval:
                    print(f"Performing double click: {current_time - self.last_click_time} > {self.click_interval}")
                    pyautogui.doubleClick()
                    self.last_click_time = current_time
                    self.last_gesture = 'double click'
                else:
                    print(f"Double click not performed: {current_time - self.last_click_time} > {self.click_interval}")

    # def perform_click_action(self):
    #     current_time = time.time()
    #     if not self.speech_recognition:  # 제스처 only 일 때
    #         if 'click' != self.last_gesture and current_time - self.last_click_time > self.click_interval:
    #             pyautogui.click()
    #     else:  # 음성 인식 모드일때
    #         if current_time - self.last_click_time > self.click_interval:
    #             pyautogui.click()
    #         else:
    #             print(f'클릭이 되지 않았음: {current_time - self.last_click_time} > {self.click_interval}')
    #     self.last_click_time = current_time
    #     self.last_gesture = 'click'
    #
    # def perform_double_click_action(self):
    #     current_time = time.time()
    #     if not self.speech_recognition:  # 제스처 only 일 때
    #         if 'double click' != self.last_gesture and current_time - self.last_click_time > self.click_interval:
    #             pyautogui.doubleClick()
    #     else:  # 음성 인식 모드일때
    #         if current_time - self.last_click_time > self.click_interval:
    #             pyautogui.doubleClick()
    #     self.last_click_time = current_time
    #     self.last_gesture = 'double click'

    def perform_scroll_action(self, gesture):
        with self.frame_lock:
            scroll_amount = self.total_screen_height // 15
            if gesture == 'up':
                print(f"Scrolling up by {scroll_amount}")
                pyautogui.scroll(scroll_amount)
                self.last_gesture = 'scroll up'
            elif gesture == 'down':
                print(f"Scrolling down by {scroll_amount}")
                pyautogui.scroll(-scroll_amount)
                self.last_gesture = 'scroll down'

    def perform_drag_action(self, gesture):
        with self.frame_lock:
            if gesture == 'drag' and not self.dragging:
                print("Starting drag...")
                pyautogui.mouseDown()
                self.dragging = True
            elif gesture == 'drop' and self.dragging:
                print("Ending drag...")
                pyautogui.mouseUp()
                self.dragging = False

    def start_gesture_recognition(self):
        self.recognition_active = True

    def stop_gesture_recognition(self):
        self.recognition_active = False

    def run(self):
        self.running = True

        capture_thread = threading.Thread(target=self.capture_frames)
        # capture_thread.daemon = True
        capture_thread.start()

        process_thread = threading.Thread(target=self.process_frames)
        # process_thread.daemon = True
        process_thread.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            capture_thread.join()
            process_thread.join()

        self.cap.release()
        cv2.destroyAllWindows()

    def capture_frames(self):
        while self.running:
            frame = self.cap.get_frame()
            if frame is not None:
                with self.frame_lock:
                    if len(self.frame_queue) == self.frame_queue.maxlen:
                        self.frame_queue.popleft()
                    self.frame_queue.append(frame)
            time.sleep(0.01)  # Slight delay to reduce CPU usage

    def process_frames(self):
        while self.running:
            with self.frame_lock:
                if self.frame_queue:
                    self.frame = self.frame_queue[-1]  # Get the latest frame

            if self.recognition_active and self.frame is not None:
                img_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                result = self.hands.process(img_rgb)
                if result.multi_hand_landmarks:
                    for i, hand_landmarks in enumerate(result.multi_hand_landmarks):
                        fingers_status = self.get_finger_status(hand_landmarks)
                        gesture = self.recognize_gesture(fingers_status)
                        self.gesture_buffer.append(gesture)

                        most_common_gesture = Counter(self.gesture_buffer).most_common(1)[0][0]
                        if most_common_gesture == 'standby':
                            self.standby_finger_pos = (hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y)
                            self.last_gesture = 'standby'

                        if most_common_gesture in ['move', 'drag', 'scroll']:
                            io_thread = threading.Thread(target=self.perform_mouse_action,
                                                         args=(
                                                             most_common_gesture, hand_landmarks.landmark))
                            io_thread.start()
                        if most_common_gesture == 'click':
                            self.perform_click_action()
                        if most_common_gesture == 'double click':
                            self.perform_double_click_action()
                        # else:
                        #     self.perform_click_action(most_common_gesture)
            time.sleep(self.poll_rate)  # Use the poll rate for sleep time

    def get_frame(self):
        with self.frame_lock:
            return self.frame

    def set_poll_rate(self, value):
        self.poll_rate = value

    def stop(self):
        self.running = False
