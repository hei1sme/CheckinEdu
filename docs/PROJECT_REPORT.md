# CheckinEdu: An AI-Powered Real-Time Student Attendance System

![CheckinEdu Logo Placeholder](assets/school_logo.png)

## Project Overview

CheckinEdu is an advanced desktop application designed to automate student attendance tracking using real-time facial recognition. Developed with a focus on efficiency, security, and user experience, it provides a seamless solution for educational institutions to manage attendance records. The system features a modern, intuitive interface inspired by FPT University's branding guidelines, ensuring a professional and engaging user interaction.

**Key Highlights:**
*   **Automated Attendance:** Replaces manual processes with accurate, real-time facial recognition.
*   **Efficient Enrollment:** Includes a streamlined batch enrollment system for administrators to quickly register multiple students.
*   **Robust Data Management:** Securely handles student, course, and attendance data.
*   **Responsive UI:** Built with CustomTkinter for a smooth and interactive user experience.

## Features

*   **Real-Time Attendance Dashboard:** Live webcam feed with dynamic feedback on attendance status.
*   **Secure Administrative Panel:** Passcode-protected access for system configuration and data management.
*   **Integrated Batch Enrollment:** Guided process for capturing and enrolling student facial data.
*   **Dynamic Course & Class Management:** Tools for administrators to organize academic structures.
*   **Advanced Face Recognition Engine:** Utilizes Haar Cascades for detection and LBPH for robust recognition.
*   **Configurable Sensitivity:** Adjustable recognition tolerance to adapt to various environmental conditions.
*   **Automated Attendance Logging:** Prevents duplicate entries and maintains accurate records in CSV format.
*   **Model Retraining Capability:** Allows for continuous improvement of recognition accuracy with new enrollment data.
*   **Intelligent Pre-processing:** Enhances image quality for optimal recognition performance.

## Technical Stack

CheckinEdu is built primarily with Python, leveraging a robust set of libraries and a clear architectural pattern:

*   **Language:** Python 3.9+
*   **UI Framework:** `CustomTkinter` for a modern and customizable graphical interface.
*   **Computer Vision:** `opencv-python` for real-time video processing, face detection (Haar Cascades), and recognition (LBPH).
*   **Image Processing:** `Pillow (PIL)` for image manipulation.
*   **Data Management:** `pandas` for CSV operations, `json` and `pickle` for structured data serialization.
*   **Environment Management:** `python-dotenv` for secure configuration.
*   **Design Pattern:** Model-View-ViewModel (MVVM) for a modular, maintainable, and scalable codebase.
    *   **Model (`src/core`):** Encapsulates business logic, data handling, and computer vision algorithms.
    *   **View (`src/ui/frames`, `src/ui/widgets`):** Manages the graphical user interface elements.
    *   **ViewModel (`src/ui/app_view_model.py`):** Acts as an intermediary, managing application state and orchestrating interactions between the View and Model.

## Getting Started

To set up and run the CheckinEdu application, please refer to the detailed [Usage Guide](docs/USAGE_GUIDE.md) in the `docs/` directory.

### Quick Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/CheckinEdu.git
    cd CheckinEdu
    ```
2.  **Create & Activate Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Admin Passcode:** Create a `.env` file in the root directory with `ADMIN_PASSCODE=your_secret_pass`.
5.  **Run the Application:**
    ```bash
    python main.py
    ```

## Documentation

For in-depth information about the project, refer to the following documents in the `docs/` directory:

*   **[Usage Guide](docs/USAGE_GUIDE.md):** Comprehensive instructions for installation, setup, and using all application features.
*   **[Function Map](docs/FUNCTION_MAP.md):** Detailed mapping of assignment requirements to specific code implementations.
*   **[CPV301 Assignment](docs/CPV301_Assignment.pdf):** The original assignment brief and requirements.

## Contributing

Contributions are welcome! Please refer to the [Contributing Guidelines](CONTRIBUTING.md) (if available) or follow standard GitHub fork/pull request workflow.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
