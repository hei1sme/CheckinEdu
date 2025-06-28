# CheckinEdu: Usage Guide

This document provides a comprehensive guide on how to set up, use, and understand the CheckinEdu application.

## 1. Project Overview

CheckinEdu is an AI-powered student attendance system leveraging facial recognition. It's designed as a standalone desktop application with a user-friendly interface, enabling efficient and automated attendance tracking for educational institutions.

## 2. Setup and Installation

To get the CheckinEdu application up and running on your system, follow these steps:

### 2.1. Prerequisites

*   **Python 3.9+:** Ensure you have a compatible version of Python installed.
*   **Webcam:** A functional webcam is required for facial recognition.
*   **Custom Fonts (Manual Installation):** For the intended visual design, you need to manually install the following font families on your operating system:
    *   `Playfair Display`
    *   `Inter`
    *   `Poppins`
    (These fonts are typically found in the `assets/fonts/` directory within the project, but they need to be installed system-wide for CustomTkinter to use them.)

### 2.2. Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/CheckinEdu.git
    cd CheckinEdu
    ```
    *(Replace `your-username` with the actual GitHub username if you've forked the repository.)*

2.  **Create a Python Virtual Environment (recommended):**
    ```bash
    python -m venv venv
    ```
    This isolates project dependencies from your system-wide Python installation.

3.  **Activate the Virtual Environment:**
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This command installs all necessary Python libraries listed in `requirements.txt`.

5.  **Configure Admin Passcode:**
    *   Create a file named `.env` in the root directory of the project (same level as `main.py`).
    *   Add your desired admin passcode to this file in the following format:
        ```
        ADMIN_PASSCODE=your_secret_pass
        ```
        Replace `your_secret_pass` with a strong, secret password. This file is ignored by Git for security.

## 3. Application Usage

### 3.1. Running the Application

To start CheckinEdu, activate your virtual environment (if not already active) and run:

```bash
python main.py
```

### 3.2. First-Time Setup

Upon the first launch, if no course or student data is found, the application will automatically direct you to the **Admin Panel**. This is where you'll perform the initial setup of your courses, classes, and student enrollments.

### 3.3. Admin Panel

The Admin Panel is the control center for CheckinEdu. It's accessible from the Main Dashboard via the "Admin Panel" button. You will be prompted to enter your `ADMIN_PASSCODE` for security.

#### 3.3.1. Course & Class Management

*   **Add Course:** Enter a course name and click "Add Course".
*   **Add Class:** Select an existing course from the dropdown, enter a class name, and click "Add Class".
*   **Delete Course:** Select a course and click "Delete Selected Course" to remove it and all its associated classes.
*   **Delete Class:** Select a course and a class, then click "Delete Selected Class" to remove a specific class.

#### 3.3.2. Student Enrollment

This section allows you to enroll new students into the system for facial recognition.

1.  **Add Student to Session:**
    *   Enter the **Student ID** (e.g., `SE194127`).
    *   Enter the **Full Name** (e.g., `Le Nguyen Gia Hung`).
    *   Select the **Class** the student belongs to.
    *   Click "Add Student to Session". The student will appear in the "Session Queue".

2.  **Capture Images for Enrollment:**
    *   Select a student from the "Session Queue" and click "Start Capture".
    *   A live camera feed will appear. Follow the on-screen prompts (e.g., "Look STRAIGHT, Neutral Expression").
    *   For each prompt, position the student's face correctly and press the **SPACEBAR** to capture an image.
    *   Capture all 8 required poses.

3.  **Re-Train Model:**
    *   After enrolling new students (and capturing their images), it is **CRUCIAL** to click the "Re-Train Model" button.
    *   This process updates the facial recognition model with the new student data, enabling the system to recognize them during attendance tracking.
    *   A message box will confirm the training completion.

#### 3.3.3. Application Settings

*   **Confirmation Threshold:** Adjust the number of consecutive frames a face must be recognized for before attendance is logged. Higher values increase accuracy but may slow down logging.
*   **Camera Index:** If you have multiple webcams, you can specify which one to use (e.g., `0` for default, `1` for the next, etc.).
*   Click "Save Settings" to apply changes.

### 3.4. Main Dashboard (Attendance Tracking)

This is the primary interface for daily attendance operations.

1.  **Select Course and Class:** Choose the relevant course and class from the dropdown menus.
2.  **Adjust Recognition Sensitivity:** Use the slider to fine-tune the recognition tolerance:
    *   **Lower values (stricter):** Reduce false positives (incorrect recognition) but may increase false negatives (missed recognition).
    *   **Higher values (looser):** Increase the chance of recognizing known faces but may also increase false positives.
3.  **Start Attendance:** Click the "Start Attendance" button to activate the live camera feed and begin real-time facial recognition.
    *   Detected faces will be highlighted with bounding boxes.
    *   Recognized students will have their status displayed (e.g., "Attended", "Already Logged", "Verifying").
    *   Attendance is automatically logged to a CSV file in `data/attendance_logs/` once a student is confirmed.
4.  **Stop Attendance:** Click the "Stop Attendance" button to pause the recognition process and turn off the camera feed.
5.  **Finish & Exit:** Click the "Finish & Exit" button to close the application.

## 4. Troubleshooting

*   **Camera Not Working:**
    *   Ensure your webcam is properly connected and not in use by another application.
    *   Check the "Camera Index" in Admin Panel settings.
    *   Verify camera drivers are up-to-date.
*   **Poor Recognition Accuracy:**
    *   Ensure good lighting conditions.
    *   Capture more diverse enrollment images (various poses, expressions).
    *   Adjust "Recognition Sensitivity" in the Main Dashboard.
    *   Re-train the model after enrolling new students.
*   **Application Freezes/Unresponsive:**
    *   This can occur if the system is under heavy load or during rapid start/stop of attendance. Ensure your system meets the minimum requirements.
    *   Restart the application.
*   **Font Display Issues:**
    *   Ensure the required custom fonts (`Playfair Display`, `Inter`, `Poppins`) are correctly installed on your operating system.

## 5. Project Structure (Simplified)

```
/CheckinEdu/
├── .gitignore
├── README.md
├── main.py
├── requirements.txt
├── .env
├── assets/
│   └── fonts/
│       └── ... (your font files)
│   └── school_logo.png
├── data/
│   ├── attendance_logs/
│   │   └── .gitkeep
│   ├── known_faces/
│   │   └── .gitkeep
│   └── system_data/
│       └── .gitkeep
├── docs/
│   ├── CPV301_Assignment.pdf
│   ├── FUNCTION_MAP.md
│   └── USAGE_GUIDE.md
└── src/
    ├── core/                   # Model (logic, data, validation)
    │   └── ...
    ├── ui/                     # View & ViewModel
    │   ├── app_view_model.py
    │   ├── frames/
    │   │   └── ...
    │   └── widgets/
    │       └── ...
```
