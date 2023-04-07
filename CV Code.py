import cv2
import numpy as np
import dlib
import time
import pandas as pd

# Initialize the camera
cap = cv2.VideoCapture(0)

# Initialize the Dlib face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Initialize the variables to track the gaze direction and the time elapsed
gaze_x = 0
gaze_y = 0
last_seen_time = time.time()
look_away_start_time = None
vid_start = time.time()
look_away_duration = 0
track_record = []
track_state = 0

# Get the screen resolution
screen_width, screen_height = 1920, 1080

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = detector(gray)

    # Loop through each face
    for face in faces:
        # Detect the landmarks of the face
        landmarks = predictor(gray, face)

        # Get the coordinates of the left and right eyes
        left_eye_coords = [(landmarks.part(36).x, landmarks.part(36).y),
                           (landmarks.part(37).x, landmarks.part(37).y),
                           (landmarks.part(38).x, landmarks.part(38).y),
                           (landmarks.part(39).x, landmarks.part(39).y),
                           (landmarks.part(40).x, landmarks.part(40).y),
                           (landmarks.part(41).x, landmarks.part(41).y)]
        right_eye_coords = [(landmarks.part(42).x, landmarks.part(42).y),
                            (landmarks.part(43).x, landmarks.part(43).y),
                            (landmarks.part(44).x, landmarks.part(44).y),
                            (landmarks.part(45).x, landmarks.part(45).y),
                            (landmarks.part(46).x, landmarks.part(46).y),
                            (landmarks.part(47).x, landmarks.part(47).y)]

        # Compute the center of the left and right eyes
        left_eye_center = np.mean(left_eye_coords, axis=0).astype(int)
        right_eye_center = np.mean(right_eye_coords, axis=0).astype(int)

        # Draw circles around the left and right eyes
        cv2.circle(frame, left_eye_center, 5, (0, 0, 255), -1)
        cv2.circle(frame, right_eye_center, 5, (0, 0, 255), -1)

        # Calculate the gaze direction
        gaze_x = ((left_eye_center[0] + right_eye_center[0]) / 2 / screen_width) * screen_width
        gaze_y = ((left_eye_center[1] + right_eye_center[1]) / 2 / screen_height) * screen_height

        # Update the last seen time
        last_seen_time = time.time()

        # Reset the look-away start time
        look_away_start_time = None
        look_away_duration = 0

    # Show the frame
    cv2.imshow('Eye tracking', frame)
    
    if time.time() - last_seen_time > 5 and track_state == 0:
        away_start_time = time.time()
        track_state = 1
    else:
        if time.time() - last_seen_time < 5 and track_state == 1:
            away_end_time = time.time()
            track_state = 0
            away_time_intervals = away_end_time - away_start_time
            time_period = away_start_time - vid_start
            track_record.append([time_period,away_time_intervals])
            print("Time intervals where the person looked away for more than 5 seconds:", time_period, away_time_intervals)

    # Wait for a key press
    key = cv2.waitKey(1)
    
    # If the 'c' key is pressed, calibrate the eye tracker
    if key == ord('c'):
        calibration_x, calibration_y = gaze_x, gaze_y
        print("Calibration complete!")
    
    # If the 'q' key is pressed, quit the program
    if key == ord('q'):
        df = pd.DataFrame(track_record, columns=["Time Period","Away Duration"])
        df.to_excel("look_away_record.xlsx", index=False)
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()




       

