import cv2
import numpy as np
import os
import pickle
from PIL import Image, ExifTags

def auto_rotate_if_landscape(img):
    h, w = img.shape[:2]
    if w > h:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    return img

def load_and_correct_orientation(image_path_or_array):
    # Accepts either a file path or a numpy array (BGR)
    if isinstance(image_path_or_array, str):
        img = Image.open(image_path_or_array)
    else:
        img = Image.fromarray(cv2.cvtColor(image_path_or_array, cv2.COLOR_BGR2RGB))
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        exif = img._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation)
            if orientation_value == 3:
                img = img.rotate(180, expand=True)
            elif orientation_value == 6:
                img = img.rotate(270, expand=True)
            elif orientation_value == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return auto_rotate_if_landscape(img)

def apply_clahe(gray_img, clipLimit=2.0, tileGridSize=(8,8)):
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
    return clahe.apply(gray_img)

# Path to Haar Cascade XML (ensure this file is in your project or use OpenCV's default path)
MODEL_PATH = "data/system_data/lbph_model.xml"
LABEL_MAP_PATH = "data/system_data/lbph_label_map.pkl"
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
FACE_SIZE = (150, 150)
KNOWN_FACES_DIR = "data/known_faces"

class HaarLBPHFaceEngine:
    def __init__(self, model_path=MODEL_PATH, label_map_path=LABEL_MAP_PATH):
        self.face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.model_path = model_path
        self.label_map_path = label_map_path
        self.label_map = {}  # label:int -> name:str
        self.reverse_label_map = {}  # name:str -> label:int
        self.load_model()

    def load_model(self):
        """Loads the trained model and label map from disk."""
        try:
            if os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 0:
                self.recognizer.read(self.model_path)
            else:
                pass
        except cv2.error as e:
            pass
            # Optionally, re-initialize recognizer or set a flag indicating failure
        except Exception as e:
            pass

        try:
            if os.path.exists(self.label_map_path):
                with open(self.label_map_path, 'rb') as f:
                    self.label_map = pickle.load(f)
                    self.reverse_label_map = {v: k for k, v in self.label_map.items()}
            else:
                pass
        except (EOFError, pickle.UnpicklingError) as e:
            self.label_map = {} # Reset to empty to prevent using corrupted data
            self.reverse_label_map = {}
        except FileNotFoundError:
            pass
        except Exception as e:
            pass

    def train_from_folder(self, known_faces_dir=KNOWN_FACES_DIR):
        faces = []
        labels = []
        label_map = {}
        label_counter = 0

        if not os.path.exists(known_faces_dir):
            raise ValueError(f"Known faces directory not found: {known_faces_dir}")

        try:
            student_folders = os.listdir(known_faces_dir)
        except OSError as e:
            raise ValueError(f"Error accessing known faces directory: {e}")

        for student_folder in student_folders:
            student_folder_path = os.path.join(known_faces_dir, student_folder)
            if not os.path.isdir(student_folder_path):
                continue
            label_map[label_counter] = student_folder
            
            try:
                for filename in os.listdir(student_folder_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(student_folder_path, filename)
                        try:
                            img = cv2.imread(image_path)
                            if img is None:
                                continue
                            # Detect face in the image
                            faces_rects = self.face_cascade.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
                            if len(faces_rects) == 0:
                                continue
                            x, y, w, h = faces_rects[0]
                            face_img = img[y:y+h, x:x+w]
                            preprocessed = self.preprocess_face(face_img)
                            faces.append(preprocessed)
                            labels.append(label_counter)
                        except Exception as e:
                            continue
            except OSError as e:
                continue
            label_counter += 1

        if not faces or not labels:
            raise ValueError("No faces or labels found for training.")
        
        try:
            self.train(faces, labels)
            self.set_label_map(label_map)
            with open(self.label_map_path, 'wb') as f:
                pickle.dump(label_map, f)
        except Exception as e:
            raise # Re-raise the exception after logging

        return len(faces)

    def train(self, faces, labels):
        # faces: list of preprocessed face images (grayscale, 150x150)
        # labels: list of int labels
        self.recognizer.train(faces, np.array(labels))
        self.recognizer.save(self.model_path)

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        return faces  # list of (x, y, w, h)

    def recognize_face(self, face_img, confidence_threshold=75):
        # face_img: preprocessed (grayscale, 150x150)
        if not self.label_map: # Check if model is trained/loaded
            return 'Unknown', 0

        label, confidence = self.recognizer.predict(face_img)

        # LBPH confidence is a distance. Lower is better.
        if confidence < confidence_threshold:
            return self.label_map.get(label, 'Unknown'), confidence
        else:
            return 'Unknown', confidence

    def preprocess_face(self, face_img):
        # face_img: cropped BGR or grayscale
        # Step 1: Orientation correction (if needed)
        if isinstance(face_img, str) or (hasattr(face_img, 'shape') and len(face_img.shape) == 3):
            face_img = load_and_correct_orientation(face_img)
        # Step 2: Grayscale
        if len(face_img.shape) == 3:
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        # Step 3: Resize
        face_img = cv2.resize(face_img, FACE_SIZE)
        # Step 4: CLAHE (adaptive histogram equalization)
        face_img = apply_clahe(face_img)
        # Step 5: Gaussian Blur
        face_img = cv2.GaussianBlur(face_img, (3, 3), 0)
        # Step 6: Sharpening
        kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        face_img = cv2.filter2D(face_img, -1, kernel)
        return face_img

    def set_label_map(self, label_map):
        self.label_map = label_map
        self.reverse_label_map = {v: k for k, v in label_map.items()}

    def train_model(self):
        """
        Scans the known_faces directory, detects and preprocesses faces, trains the recognizer,
        and saves both the model and label map. Returns the number of faces encoded.
        """
        return self.train_from_folder(known_faces_dir=KNOWN_FACES_DIR)
