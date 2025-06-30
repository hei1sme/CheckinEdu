import os
import cv2
import numpy as np
from src.core.face_engine_haar_lbph import load_and_correct_orientation, apply_clahe, FACE_SIZE

KNOWN_FACES_DIR = "data/known_faces"

def preprocess_and_save(face_img_path, save_path):
    img = load_and_correct_orientation(face_img_path)
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, FACE_SIZE)
    img = apply_clahe(img)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)
    cv2.imwrite(save_path, img)

def batch_preprocess_known_faces():
    for student_folder in os.listdir(KNOWN_FACES_DIR):
        student_path = os.path.join(KNOWN_FACES_DIR, student_folder)
        if not os.path.isdir(student_path):
            continue
        for filename in os.listdir(student_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(student_path, filename)
                preprocess_and_save(img_path, img_path)  # Overwrite original

if __name__ == "__main__":
    batch_preprocess_known_faces()
    print("Batch preprocessing of known faces completed.")