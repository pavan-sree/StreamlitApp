import streamlit as st
import mediapipe as mp
import math
import time
import cv2
import serial.tools.list_ports
import serial
from sounds import get_base64_of_audio,sound_file,error_file

def activate_serial():
    st.write('please wait...')

    def find_arduino_port():
        ports = list(serial.tools.list_ports.comports())
        
        for port in ports:
            if 'Arduino Uno' in port.description:
                return port.device
        
        return None

    def connect_to_arduino():
        arduino_port = find_arduino_port()
        
        if arduino_port:
            try:
                ser = serial.Serial(arduino_port, 9600)  # Adjust baudrate if needed
                time.sleep(2)  # Allow time for Arduino to initialize
                print(f"Connected to Arduino on port {arduino_port}")
                audio_base64 = get_base64_of_audio(sound_file)
                html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay="autoplay" type="audio/mpeg" />'
                st.markdown(html, unsafe_allow_html=True)
                return ser
            except serial.SerialException as e:
                print(f"Failed to connect to Arduino on port {arduino_port}: {e}")
        else:
            audio_base64 = get_base64_of_audio(error_file)
            html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay="autoplay" type="audio/mpeg" />'
            st.markdown(html, unsafe_allow_html=True)
            st.write("Arduino Uno not found.")
        
        return None

    ser = connect_to_arduino()
        
    if ser:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands()
        handCounter = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
        mp_drawing = mp.solutions.drawing_utils

        # Camera parameters (replace these with your actual values)
        known_width = 20  # Width of an object in the scene (in centimeters)
        focal_length = 1000  # Focal length of the camera (in pixels)
        grip = None
        record = 0
        loop = []
        positions = []
        flag = 0
        count = 0
        x=0
        y=0
        z=0
        w = 0
        lock = 0
        # OpenCV setup
        cap = cv2.VideoCapture(0)  # You can change the index if you have multiple cameras

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
                    index_finger_folded = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].y \
                                 > hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y

                    # Update grip variable
                    if (middle_finger_folded and ring_finger_folded):
                        grip = 0
                    else:
                        grip = 90
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
                            if(lock==0):
                                x = distance_to_top
                                y = distance_to_right
                                z = grip
                                message = f"{int(distance)},{int(distance_to_top/2)},{int(grip)},{int(distance_to_right)*10}\n"
                                ser.write(message.encode())
                                print(message)
                                if(index_finger_folded):
                                    w = x
                                    lock = 1
                                    print("locked")
                                    cv2.putText(frame, f"Elbow lock activated", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                (255, 255, 255), 2)
                                else:
                                    lock = 0
                                    print("unlocked")
                            if(lock==1):
                                x = w
                                message = f"{int(distance)},{int(x / 2)},{int(grip)},{int(distance_to_right)*10}\n"
                                ser.write(message.encode())
                                print(message)
                                if (index_finger_folded):
                                    x = w
                                    lock = 1
                                    print("locked")
                                    cv2.putText(frame, f"Elbow lock activated", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                (255, 255, 255), 2)
                                else:
                                    lock = 0
                                    print("unlocked")
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
                        message = f"{a1},{b1},{c1},{d1}\n"
                        ser.write(message.encode())
                        time.sleep(1)
                        print(message)
                print("stopped")
                flag = 0



            cv2.imshow("Hand Tracking", frame)

            # Break the loop if 'q' key is pressed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        # Release the VideoCapture and close all OpenCV windows
        cap.release()
        cv2.destroyAllWindows()
        

            
        ser.close()
