import cv2
import mediapipe as mp
from controller import Controller


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Webcam not found or cannot be opened.")
        return

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    print("Hand Controller Started")
    print("Press ESC to exit.")

    while True:
        success, img = cap.read()

        if not success or img is None:
            print("Error: Failed to read frame from webcam.")
            break

        img = cv2.flip(img, 1)

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]

            Controller.hand_landmarks = hand_landmarks

            mp_draw.draw_landmarks(
                img,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            Controller.update_fingers_status()
            Controller.cursor_moving()
            Controller.detect_scrolling()
            Controller.detect_zooming()
            Controller.detect_clicking()
            Controller.detect_dragging()

        else:
            Controller.reset_when_no_hand()

        cv2.imshow("Hand Tracker", img)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()


if __name__ == "__main__":
    main()