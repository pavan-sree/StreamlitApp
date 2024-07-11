import streamlit as st
import bluetooth
import mediapipe as mp
import math
import time
import cv2
from sounds import get_base64_of_audio,sound_file,error_file

def activate_camera():
    st.write("please wait...")
    class BluetoothConnectionManager:
            def __init__(self):
                self.socket = None

            def connect_to_hc05(self):
                nearby_devices = bluetooth.discover_devices()
                hc05_address = None
                for address in nearby_devices:
                    if bluetooth.lookup_name(address) == "HC-05":
                        hc05_address = address
                        break

                if hc05_address is None:
                    print("HC-05 device not found.")
                    return False

                try:
                    self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    self.socket.connect((hc05_address, 1))  # Port 1 is usually used for serial communication
                    print("Connected to HC-05.")
                    audio_base64 = get_base64_of_audio(sound_file)
                    html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay="autoplay" type="audio/mpeg" />'
                    st.markdown(html, unsafe_allow_html=True)
                    return True
                except Exception as e:
                    print("Failed to connect to HC-05:", e)
                    return False

            def send_data(self, data):
                if self.socket is not None:
                    try:
                        self.socket.send(data)
                        print("Data sent successfully:", data)
                    except Exception as e:
                        print("Error sending data:", e)
                        BluetoothConnectionManager()
                else:
                    print("Not connected to HC-05.")

            def close_connection(self):
                if self.socket is not None:
                    self.socket.close()
                    print("Connection closed.")
                else:
                    print("Not connected to HC-05.")


# Create an instance of BluetoothConnectionManager
    bluetooth_manager = BluetoothConnectionManager()

    # Connect to HC-05
    if bluetooth_manager.connect_to_hc05():
        # Hand tracking setup
        st.write("Bluetooth connected please wait....")
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands()
        mp_drawing = mp.solutions.drawing_utils
        handCounter = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

        known_width = 20
        focal_length = 1000
        grip = None
        record = 0
        loop = []
        positions = []
        flag = 0
        x=0
        y=0
        z=0
        count = 0
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe Hands
            results = hands.process(rgb_frame)

            # Check if hands are detected
            if results.multi_hand_landmarks:
                # Iterate through detected hands
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks on the image with green color (0, 255, 0)
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0)))
                    # Draw connections between landmarks with red color (0, 0, 255)
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255)))
                    num_hands = len(results.multi_hand_landmarks)
                    # Get the width of the hand in pixels
                    hand_width_pixels = (hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x - \
                                        hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y) * -1

                    angle_rad = (math.atan2(
                        hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y,
                        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].x -
                        hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x))

                    # Calculate the distance using the formula
                    distance = (((known_width * focal_length) / hand_width_pixels) / 10000) * 10
                    angle_deg = math.degrees(angle_rad)
                    if (distance > 850 or distance < 0):
                        if (distance > 850):
                            distance = 800
                        else:
                            distance = 0

                    middle_finger_folded = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP].y \
                                   < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
                    ring_finger_folded = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP].y \
                                        < hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y
                    pinky_finger_folded = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP].y > hand_landmarks.landmark[
                        mp_hands.HandLandmark.PINKY_PIP].y

                    # Update grip variable
                    if (middle_finger_folded and ring_finger_folded):
                        grip = 90
                    else:
                        grip = 0
                    if (pinky_finger_folded):
                        record = 0
                    else:
                        record = 1
                    # Display the distance on the frame

                    top_of_screen = 0  # Assuming the top of the screen is at y-coordinate 0
                    right_of_screen = 0
                    wrist_y = (int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * frame.shape[0]))
                    wrist_x = (int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * frame.shape[0]))
                    distance_to_right = (int((right_of_screen - wrist_x + 360 / 10))*-1)/10
                    distance_to_top = int((top_of_screen - wrist_y + 360) / 10)
                    distance = 0
                    if( distance_to_top < 0 ):
                        distance_to_top = 0

                    if(num_hands > 1):
                        cv2.putText(frame, f"use one hand to control", (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    else:
                        cv2.putText(frame, f"Distance to Top: {distance_to_top} pixels", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        cv2.putText(frame, f"Distance to Right: {int(distance_to_right)} degrees", (10, 70),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        cv2.putText(frame, f"Grip: {grip}", (10, 110),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        cv2.putText(frame, f"count: {num_hands}", (10, 180),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        count+=1
                        if(count == 20):
                            message = f"{int(distance)},{int(distance_to_top)},{int(grip)},{int(distance_to_right)}\n"
                            bluetooth_manager.send_data(message)
                            print(message)
                            x = distance_to_top
                            y = distance_to_right
                            z = grip
                            count = 0
                            
                        
                      
                      
                    if( pinky_finger_folded and num_hands == 1):
                        flag = 1
                        print("recording")
                        cv2.putText(frame, f"recording position saved", (10, 190),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        positions.append(int(distance))
                        positions.append(int(distance_to_top))
                        positions.append(int(grip))
                        positions.append(int(distance_to_right))
                        loop.append(list(positions))
                        print(loop)
                        positions.clear()
                        print("recording stopped")
            elif(flag == 1):
                cv2.putText(frame, f"mimicing...", (100, 190),
                            cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 2)
                print("this is the recorded")

                for i in range(0, len(loop)):
                        a1 = loop[i][0]
                        b1 = loop[i][1]
                        c1 = loop[i][2]
                        d1 = loop[i][3]
                        message = f"{a1},{b1*10},{c1},{d1*10}\n"
                        bluetooth_manager.send_data(message) 
                        print(message)
                print("stopped")
                flag = 0

            cv2.imshow("Hand Tracking", frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        # Close the connection after hand tracking is done
        bluetooth_manager.close_connection()
    else:
        print("Failed to connect to HC-05.")
        audio_base64 = get_base64_of_audio(error_file)
        html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay="autoplay" type="audio/mpeg" />'
        st.markdown(html, unsafe_allow_html=True)
        st.write("HC-05 not found please try again...")