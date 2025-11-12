import cv2
import mediapipe as mp
import os

# Initialize MediaPipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def process_static_images(image_files, output_dir="annotated_images"):
    """
    Processes a list of static image files to detect and draw hand landmarks.
    
    Args:
        image_files (list): A list of file paths to the images.
        output_dir (str): The directory to save annotated images.
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Processing {len(image_files)} static image(s)...")

    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5) as hands:
        
        for idx, file in enumerate(image_files):
            if not os.path.exists(file):
                print(f"Warning: File not found, skipping: {file}")
                continue
                
            # Read an image, flip it around y-axis for correct handedness output
            image = cv2.flip(cv2.imread(file), 1)
            # Convert the BGR image to RGB before processing
            results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            # Print handedness
            print(f'\n--- Image: {file} ---')
            print('Handedness:', results.multi_handedness)

            if not results.multi_hand_landmarks:
                print("No hands detected.")
                continue

            image_height, image_width, _ = image.shape
            annotated_image = image.copy()

            # Draw hand landmarks
            for hand_landmarks in results.multi_hand_landmarks:
                print('Hand landmarks:')
                # Example: Print index finger tip coordinates
                print(
                    f'Index finger tip: (',
                    f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
                    f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
                )
                
                mp_drawing.draw_landmarks(
                    annotated_image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
            
            # Save the annotated image
            output_path = os.path.join(output_dir, f'annotated_image_{idx}.png')
            cv2.imwrite(output_path, cv2.flip(annotated_image, 1))
            print(f'Saved annotated image to: {output_path}')

            # Draw hand world landmarks (3D plot)
            if results.multi_hand_world_landmarks:
                print("Plotting 3D world landmarks...")
                for hand_world_landmarks in results.multi_hand_world_landmarks:
                    mp_drawing.plot_landmarks(
                        hand_world_landmarks, mp_hands.HAND_CONNECTIONS, azimuth=5)

    print("\nStatic image processing complete.")


def run_webcam_detection(camera_index=0):
    """
    Launches webcam detection for hands in real-time.
    
    Args:
        camera_index (int): The index of the camera to use (default is 0).
    """
    print("Starting webcam detection... Press 'ESC' to quit.")
    cap = cv2.VideoCapture(camera_index)

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # To improve performance, mark the image as not writeable
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            # Draw the hand annotations on the image
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
            
            # Flip the image horizontally for a selfie-view display
            cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
            
            # Exit loop when 'ESC' key is pressed
            if cv2.waitKey(5) & 0xFF == 27:
                break
                
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam detection stopped.")


