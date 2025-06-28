# FUNCTION_MAP.md: CPV301 Assignment Implementation Mapping

This document maps the core functions required by the CPV301 Assignment to their implementation within the CheckinEdu project codebase. Each section details where the functionality resides and provides a brief explanation of its operation.

## 1. Function 1: Stream video from IP camera to computer (Local Webcam Allowed)

*   **Assignment Requirement:** Use IP camera as input device and RTSP protocol to stream video to computer. (Clarification: Local webcam is allowed for this project).
*   **Implementation Status:** MET
*   **Code Files & Summary:**
    *   `src/ui/widgets/video_capture.py`
        *   **`VideoCapture` class:** This custom CustomTkinter widget is responsible for initializing and managing the webcam feed. The `start_capture()` method uses `cv2.VideoCapture(self.view_model.camera_index)` to open the camera. The `_update_frame()` method continuously reads frames from the camera and displays them in the UI. The `camera_index` is configurable via the Admin Panel settings.

## 2. Function 2: Cropped the video into image frames

*   **Assignment Requirement:** The video will be cropped into image frames, depending on the capture rate and resolution of the camera. The result of this step is an image containing the student's face.
*   **Implementation Status:** MET
*   **Code Files & Summary:**
    *   `src/ui/app_view_model.py`
        *   **`capture_image_for_enrollment()` method:** During student enrollment, this method takes a full video frame, uses `self.face_engine.detect_faces()` to find face coordinates, and then crops the `face_img` from the original frame (`face_img = frame[y:y+h, x:x+w]`). This ensures only the face region is saved for training.
    *   `src/core/face_engine_haar_lbph.py`
        *   **`train_from_folder()` method:** When the model is retrained, this method reads the saved (already cropped) images from `data/known_faces/`. It also contains logic to detect and crop faces (`face_img = img[y:y+h, x:x+w]`) from images if they were not pre-cropped, ensuring the LBPH model always trains on cropped face images.

## 3. Function 3: Face detection

*   **Assignment Requirement:** From the input image, detect the student's face position in the photo. The result of this step is a student's facial image.
*   **Implementation Status:** MET
*   **Code Files & Summary:**
    *   `src/core/face_engine_haar_lbph.py`
        *   **`detect_faces(self, frame)` method:** This method is the core of face detection. It utilizes `self.face_cascade.detectMultiMultiScale()` (which is an OpenCV Haar Cascade classifier) to identify the bounding box coordinates (`x, y, w, h`) of faces within a given `frame` (or image). It returns a list of these bounding boxes.
    *   `src/ui/app_view_model.py`
        *   **`capture_image_for_enrollment()` method:** Calls `self.face_engine.detect_faces()` to find faces before cropping and saving during enrollment.
        *   **`_recognition_worker()` method:** Calls `self.face_engine.detect_faces()` on each video frame to find faces for real-time recognition.

## 4. Function 4: Face recognition

*   **Assignment Requirement:** From the student's face image, the system will recognize the student number, name and date and time of class.
*   **Implementation Status:** MET
*   **Code Files & Summary:**
    *   `src/core/face_engine_haar_lbph.py`
        *   **`recognize_face(self, face_img, confidence_threshold)` method:** This method takes a pre-processed face image and uses the trained LBPH recognizer (`self.recognizer.predict(face_img)`) to predict the `label` (student ID) and `confidence` score. It then maps the label back to the student's name using the loaded `label_map`.
    *   `src/ui/app_view_model.py`
        *   **`_recognition_worker()` method:** After detecting and pre-processing a face, this method calls `self.face_engine.recognize_face()` to identify the student. It then manages the `recognition_buffer` for confirmation and, upon successful confirmation, calls `attendance_manager.log_attendance()`.
    *   `src/core/attendance_manager.py`
        *   **`log_attendance(student_info, course_name, class_name)` function:** This function is responsible for recording the recognized student's attendance. It parses the `student_info` (which includes student ID and name), retrieves the current date and time, and writes this information to a course-specific CSV file in `data/attendance_logs/`. It also includes logic to prevent duplicate entries for the same student on the same day.

## 5. Pre-processing

*   **Assignment Requirement:** Perform pre-processing steps such as light balance, noise filtering.
*   **Implementation Status:** MET
*   **Code Files & Summary:**
    *   `src/core/face_engine_haar_lbph.py`
        *   **`preprocess_face(self, face_img)` method:** This method applies a series of image processing steps to a given face image to enhance it for recognition. These steps include:
            *   Conversion to grayscale (`cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)`).
            *   Resizing to a standard `FACE_SIZE` (150x150 pixels).
            *   Histogram Equalization (`cv2.equalizeHist`) for light balance and contrast enhancement.
            *   Gaussian Blur (`cv2.GaussianBlur`) for noise reduction.
            *   Sharpening (`cv2.filter2D`) to enhance facial features.

