import time
import math
import pyautogui


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01


class Controller:
    hand_landmarks = None
    prev_hand = None

    screen_width, screen_height = pyautogui.size()

    index_finger_up = False
    middle_finger_up = False
    ring_finger_up = False
    little_finger_up = False
    thumb_finger_up = False

    index_finger_down = False
    middle_finger_down = False
    ring_finger_down = False
    little_finger_down = False
    thumb_finger_down = False

    all_fingers_up = False
    all_fingers_down = False

    left_clicked = False
    right_clicked = False
    double_clicked = False
    dragging = False

    last_scroll_time = 0
    last_zoom_time = 0

    scroll_delay = 0.35
    zoom_delay = 0.35

    @staticmethod
    def distance(point1, point2):
        x1 = Controller.hand_landmarks.landmark[point1].x
        y1 = Controller.hand_landmarks.landmark[point1].y
        x2 = Controller.hand_landmarks.landmark[point2].x
        y2 = Controller.hand_landmarks.landmark[point2].y

        return math.hypot(x2 - x1, y2 - y1)

    @staticmethod
    def update_fingers_status():
        lm = Controller.hand_landmarks.landmark

        Controller.index_finger_up = lm[8].y < lm[6].y
        Controller.middle_finger_up = lm[12].y < lm[10].y
        Controller.ring_finger_up = lm[16].y < lm[14].y
        Controller.little_finger_up = lm[20].y < lm[18].y

        Controller.index_finger_down = not Controller.index_finger_up
        Controller.middle_finger_down = not Controller.middle_finger_up
        Controller.ring_finger_down = not Controller.ring_finger_up
        Controller.little_finger_down = not Controller.little_finger_up

        Controller.thumb_finger_up = lm[4].x > lm[3].x
        Controller.thumb_finger_down = not Controller.thumb_finger_up

        Controller.all_fingers_up = (
            Controller.index_finger_up and
            Controller.middle_finger_up and
            Controller.ring_finger_up and
            Controller.little_finger_up
        )

        Controller.all_fingers_down = (
            Controller.index_finger_down and
            Controller.middle_finger_down and
            Controller.ring_finger_down and
            Controller.little_finger_down
        )

    @staticmethod
    def get_position(hand_x, hand_y):
        current_x = int(hand_x * Controller.screen_width)
        current_y = int(hand_y * Controller.screen_height)

        if Controller.prev_hand is None:
            Controller.prev_hand = (current_x, current_y)
            return pyautogui.position()

        old_x, old_y = pyautogui.position()

        delta_x = current_x - Controller.prev_hand[0]
        delta_y = current_y - Controller.prev_hand[1]

        Controller.prev_hand = (current_x, current_y)

        sensitivity = 1.5

        new_x = old_x + delta_x * sensitivity
        new_y = old_y + delta_y * sensitivity

        margin = 10

        new_x = max(margin, min(Controller.screen_width - margin, new_x))
        new_y = max(margin, min(Controller.screen_height - margin, new_y))

        return int(new_x), int(new_y)

    @staticmethod
    def cursor_moving():
        if Controller.hand_landmarks is None:
            return

        # Use middle of hand as stable cursor control point
        control_point = 9

        hand_x = Controller.hand_landmarks.landmark[control_point].x
        hand_y = Controller.hand_landmarks.landmark[control_point].y

        x, y = Controller.get_position(hand_x, hand_y)

        # Freeze cursor when all fingers are up and thumb is down
        cursor_frozen = Controller.all_fingers_up and Controller.thumb_finger_down

        if not cursor_frozen:
            pyautogui.moveTo(x, y, duration=0)

    @staticmethod
    def detect_scrolling():
        current_time = time.time()

        if current_time - Controller.last_scroll_time < Controller.scroll_delay:
            return

        scroll_up = (
            Controller.index_finger_down and
            Controller.middle_finger_down and
            Controller.ring_finger_down and
            Controller.little_finger_up
        )

        scroll_down = (
            Controller.index_finger_up and
            Controller.middle_finger_down and
            Controller.ring_finger_down and
            Controller.little_finger_down
        )

        if scroll_up:
            pyautogui.scroll(5)
            Controller.last_scroll_time = current_time
            print("Scrolling Up")

        elif scroll_down:
            pyautogui.scroll(-5)
            Controller.last_scroll_time = current_time
            print("Scrolling Down")

    @staticmethod
    def detect_zooming():
        current_time = time.time()

        if current_time - Controller.last_zoom_time < Controller.zoom_delay:
            return

        zoom_gesture = (
            Controller.index_finger_up and
            Controller.middle_finger_up and
            Controller.ring_finger_down and
            Controller.little_finger_down
        )

        if not zoom_gesture:
            return

        index_middle_distance = Controller.distance(8, 12)

        if index_middle_distance < 0.05:
            pyautogui.hotkey("ctrl", "-")
            Controller.last_zoom_time = current_time
            print("Zoom Out")

        else:
            pyautogui.hotkey("ctrl", "+")
            Controller.last_zoom_time = current_time
            print("Zoom In")

    @staticmethod
    def detect_clicking():
        thumb_index_distance = Controller.distance(4, 8)
        thumb_middle_distance = Controller.distance(4, 12)
        thumb_ring_distance = Controller.distance(4, 16)

        click_threshold = 0.045

        left_click_condition = (
            thumb_index_distance < click_threshold and
            Controller.middle_finger_up and
            Controller.ring_finger_up and
            Controller.little_finger_up
        )

        right_click_condition = (
            thumb_middle_distance < click_threshold and
            Controller.index_finger_up and
            Controller.ring_finger_up and
            Controller.little_finger_up
        )

        double_click_condition = (
            thumb_ring_distance < click_threshold and
            Controller.index_finger_up and
            Controller.middle_finger_up and
            Controller.little_finger_up
        )

        if left_click_condition and not Controller.left_clicked:
            pyautogui.click(button="left")
            Controller.left_clicked = True
            print("Left Click")

        elif thumb_index_distance > click_threshold:
            Controller.left_clicked = False

        if right_click_condition and not Controller.right_clicked:
            pyautogui.click(button="right")
            Controller.right_clicked = True
            print("Right Click")

        elif thumb_middle_distance > click_threshold:
            Controller.right_clicked = False

        if double_click_condition and not Controller.double_clicked:
            pyautogui.doubleClick()
            Controller.double_clicked = True
            print("Double Click")

        elif thumb_ring_distance > click_threshold:
            Controller.double_clicked = False

    @staticmethod
    def detect_dragging():
        drag_condition = Controller.all_fingers_down

        if drag_condition and not Controller.dragging:
            pyautogui.mouseDown(button="left")
            Controller.dragging = True
            print("Dragging Started")

        elif not drag_condition and Controller.dragging:
            pyautogui.mouseUp(button="left")
            Controller.dragging = False
            print("Dragging Stopped")

    @staticmethod
    def reset_when_no_hand():
        Controller.prev_hand = None

        if Controller.dragging:
            pyautogui.mouseUp(button="left")
            Controller.dragging = False

        Controller.left_clicked = False
        Controller.right_clicked = False
        Controller.double_clicked = False