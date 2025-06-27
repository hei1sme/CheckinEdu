import face_recognition
import pickle
import os
import cv2
import numpy as np

KNOWN_FACES_DIR = "data/known_faces"
MODEL_PATH = "data/system_data/encoded_faces.pkl"

def encode_known_faces():
    """
    Scans the known_faces directory, encodes all images, and saves the
    encodings to a pickle file.
    """
    print("Training in progress...")
    known_face_encodings = []
    known_face_names = []

    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)

    for student_folder in os.listdir(KNOWN_FACES_DIR):
        student_folder_path = os.path.join(KNOWN_FACES_DIR, student_folder)
        if not os.path.isdir(student_folder_path):
            continue
            
        # student_folder name is the student's ID and Name
        # e.g., "SE194127_LeNguyenGiaHung"
        for filename in os.listdir(student_folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(student_folder_path, filename)
                
                try:
                    # Load image
                    image = face_recognition.load_image_file(image_path)
                    
                    # Find face encodings
                    # We assume one face per enrollment image for simplicity
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        # Add the first found encoding to our list
                        known_face_encodings.append(encodings[0])
                        known_face_names.append(student_folder)
                    else:
                        print(f"Warning: No face found in {filename}. Skipping.")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    # Save the encodings
    data = {"encodings": known_face_encodings, "names": known_face_names}
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(data, f)
        
    print("Training complete.")
    return len(known_face_names)

def recognize_faces_in_frame(frame, known_encodings, known_names, tolerance=0.6):
    """
    Takes a video frame and returns a list of names and locations of recognized faces.
    """
    # Find all face locations and encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    recognized_faces = []
    for face_encoding, face_location in zip(face_encodings, face_locations):
        name = "Unknown"
        
        if known_encodings:
            # See if the face is a match for the known faces
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=tolerance)
            
            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                name = known_names[best_match_index]
        
        recognized_faces.append((name, face_location))
        
    return recognized_faces