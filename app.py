import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time

if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to_detector():
    st.session_state.page = "detector"

def go_home():
    st.session_state.page = "home"

if st.session_state.page == "home":
    st.title("🤰 BumpBot - Smart Exercise Safety for Pregnancy")
    st.markdown(""" 
    Welcome to **BumpBot**, your AI-powered Prenatal Workout Buddy!
                
    Select your **current trimester** and **exercise** and you BumpBot Buddy will give you **real-time posture feedback** via your webcam
                """)
    
    st.session_state.trimester = st.selectbox("Select Your Trimester", ["First Trimester", "Second Trimester", "Third Trimester"])

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.session_state.exercise = st.selectbox("Choose an Exercise", ["Squats", "Lunges", "Bird Dog", "Modified Side Plank"])
    st.button("Start", on_click=go_to_detector)

elif st.session_state.page == "detector":
    st.title(f"Exercise: {st.session_state.exercise}")
    st.caption(f"Trimester: {st.session_state.trimester}")

    st.button("Back", on_click=go_home)

    # MediaPipe pose setup
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

    stframe = st.empty()

   # OpenCV webcam
    cap = cv2.VideoCapture(0)
    last_alert_time = 0
    cooldown = 3

    def calculate_angle(a,b,c):
        a=np.array(a) #hip
        b=np.array(b) #knee
        c=np.array(c) #ankle

        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0 / np.pi)

        if angle >180.0:
         angle=360-angle
        return angle
    

    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            st.warning("Webcam not accessible.")
            break

        bump_stage=""
        # Flip for selfie-view
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:
            mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            landmarks = result.pose_landmarks.landmark

            if st.session_state.exercise == "Bird Dog":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                hip= [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                arm_straight = abs(shoulder[1]-wrist[1])<0.05
                leg_straight = abs(hip[1]-ankle[1])<0.05

                if arm_straight and leg_straight:
                    status = "Safe Bird Dog Position!"
                    color = (0, 255, 0)
                else:
                    status = "Unsafe! Keep arm/leg straight"
                    color = (0, 0, 255)

                cv2.putText(frame, status, (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2 , cv2.LINE_AA)
                



            if st.session_state.exercise == "Squats":
                hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                angle = calculate_angle(hip, knee, ankle)

                cv2.putText(frame, str(round(angle,2)), tuple(np.multiply(knee, [frame.shape[1], frame.shape[0]]).astype(int)),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255), 2, cv2.LINE_AA)

                bump_stage = st.session_state
                if bump_stage == "First Trimester":
                    squat_threshold = 90
                elif bump_stage == "Second Trimester":
                    squat_threshold=100
                else:
                    squat_threshold=110

                current_time=time.time()
                if angle<squat_threshold:
                    status = "Unsafe Squat - Too Low!"
                    color = (0,0,255)
                    
                else:
                    status = "Safe Squat"
                    color = (0,255,0)

                cv2.putText(frame, status, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
       



         
        stframe.image(frame, channels="BGR")

    cap.release()




