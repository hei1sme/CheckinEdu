<br/>
<p align="center">
  <a href="https://github.com/hei1sme/CheckinEdu">
    <!-- IMPORTANT: Update this logo path -->
    <img src="assets/logo.png" alt="CheckinEdu Logo" width="120" height="120">
  </a>

  <h1 align="center">CheckinEdu: AI-Powered Student Attendance</h1>

  <p align="center">
    An intelligent desktop application for automated student attendance tracking using real-time facial recognition.
    <br />
    <a href="https://github.com/hei1sme/CheckinEdu/blob/main/docs/USAGE_GUIDE.md"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/hei1sme/CheckinEdu/issues">Report Bug</a>
    ·
    <a href="https://github.com/hei1sme/CheckinEdu/issues">Request Feature</a>
  </p>
</p>

<!-- BADGES -->
<p align="center">
    <!-- Build Status -->
    <a href="https://github.com/hei1sme/CheckinEdu/actions/workflows/main.yml">
        <img src="https://img.shields.io/github/actions/workflow/status/hei1sme/CheckinEdu/main.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white" alt="Build Status">
    </a>
    <!-- Code Quality -->
    <a href="https://sonarcloud.io/summary/new_code?id=your-org_your-repo">
        <img src="https://img.shields.io/sonar/quality_gate/your-org_your-repo?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge&logo=sonarcloud" alt="Quality Gate">
    </a>
    <!-- License -->
    <a href="https://github.com/hei1sme/CheckinEdu/blob/main/LICENSE">
        <img src="https://img.shields.io/github/license/hei1sme/CheckinEdu?style=for-the-badge" alt="License">
    </a>
    <!-- Python Version -->
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
    <br/>
    <!-- Stars & Forks -->
    <img src="https://img.shields.io/github/stars/hei1sme/CheckinEdu?style=social" alt="Stars">
    <img src="https://img.shields.io/github/forks/hei1sme/CheckinEdu?style=social" alt="Forks">
</p>

---

## Table of Contents

- [About The Project](#about-the-project)
- [✨ Key Features](#-key-features)
- [📸 Screenshots](#-screenshots)
- [🛠️ Tech Stack & Architecture](#️-tech-stack--architecture)
  - [Architectural Pattern](#architectural-pattern)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [📖 Usage](#-usage)
- [🏗️ Project Structure](#️-project-structure)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)
- [📞 Contact](#-contact)
- [Acknowledgements](#acknowledgements)

---

## About The Project

![CheckinEdu Dashboard Placeholder](assets/dashboard_screenshot.png)
> *A placeholder for a screenshot of the main application dashboard.*

**CheckinEdu** is an advanced desktop application designed to automate student attendance tracking using real-time facial recognition. Developed with a focus on efficiency, security, and user experience, it provides a seamless solution for educational institutions. The system features a modern, intuitive interface inspired by FPT University's branding guidelines, ensuring a professional and engaging user interaction.

This project eliminates the need for manual roll calls, reducing administrative overhead and providing accurate, tamper-proof attendance records.

---

## ✨ Key Features

*   👩‍🏫 **Real-Time Attendance Dashboard:** Live webcam feed with dynamic feedback on attendance status (recognized, not recognized, already checked-in).
*   🔐 **Secure Administrative Panel:** Passcode-protected access for system configuration, data management, and model retraining.
*   批量 **Integrated Batch Enrollment:** A streamlined, guided process for capturing and enrolling facial data for multiple students at once.
*   ⚙️ **Dynamic Course & Class Management:** Intuitive tools for administrators to create, update, and manage academic structures.
*   🧠 **Advanced Face Recognition Engine:** Utilizes Haar Cascades for reliable detection and Local Binary Patterns Histograms (LBPH) for robust recognition.
*   🎯 **Configurable Sensitivity:** Adjustable recognition tolerance to adapt to various lighting and environmental conditions.
*   💾 **Automated Attendance Logging:** Prevents duplicate entries and maintains accurate, timestamped records in CSV format for easy export and analysis.
*   🔄 **Model Retraining Capability:** Allows for continuous improvement of recognition accuracy as new students are enrolled.

---

## 📸 Screenshots

A picture is worth a thousand words. Here's a glimpse into the CheckinEdu application.

| Main Dashboard                                      | Admin Panel                                      | Batch Enrollment                                  |
| --------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------- |
| ![Dashboard Placeholder](assets/dashboard_view.png) | ![Admin Panel Placeholder](assets/admin_panel.png) | ![Enrollment Placeholder](assets/enroll_process.png) |
| *Live attendance tracking in action.*               | *Secure access to system management tools.*      | *Guided process for registering new students.*      |

### Demo

<!-- IMPORTANT: Create a GIF of your app in action and place it here -->
![CheckinEdu Demo GIF](assets/app_demo.gif)
> *A short GIF demonstrating the main workflow: launching the app, recognizing a student, and marking them as present.*

---

## 🛠️ Tech Stack & Architecture

CheckinEdu is built with a modern Python stack, emphasizing a clean and scalable architecture.

| Category                | Technology / Library                                                              |
| ----------------------- | --------------------------------------------------------------------------------- |
| **Language**            | `Python 3.9+`                                                                     |
| **UI Framework**        | `CustomTkinter`                                                                   |
| **Computer Vision**     | `OpenCV-Python` (Haar Cascades, LBPH)                                             |
| **Image Processing**    | `Pillow (PIL)`                                                                    |
| **Data Management**     | `Pandas`, `JSON`, `Pickle`                                                        |
| **Environment**         | `python-dotenv`                                                                   |

### Architectural Pattern

The project follows the **Model-View-ViewModel (MVVM)** design pattern to ensure a clear separation of concerns, making the codebase modular, maintainable, and scalable.

*   **Model (`src/core`):** Encapsulates the core business logic, data handling (CSV, JSON), and the heavy-lifting computer vision algorithms. It is completely independent of the UI.
*   **View (`src/ui`):** Comprises all the graphical user interface elements (windows, frames, widgets). It's responsible for displaying data and capturing user input.
*   **ViewModel (`src/ui/app_view_model.py`):** Acts as the bridge between the View and the Model. It manages the application's state, handles user interactions, and prepares data for display.

---

## 🚀 Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

Ensure you have the following installed on your system:
*   Python 3.9 or higher
*   pip (Python package installer)
*   Git

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/hei1sme/CheckinEdu.git
    cd CheckinEdu
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # Create the environment
    python -m venv venv

    # Activate it
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure your environment:**
    Create a `.env` file in the root directory and add your admin passcode.
    ```env
    ADMIN_PASSCODE=your_secret_passcode
    ```

5.  **Run the application:**
    ```sh
    python main.py
    ```

---

## 📖 Usage

Once the application is running, you can:
1.  **Start Attendance:** The main screen will activate the camera for real-time recognition.
2.  **Access Admin Panel:** Enter your configured passcode to manage students, courses, and system settings.
3.  **Enroll Students:** Use the guided batch enrollment process to add new faces to the system.

For a comprehensive guide on all features, please refer to the **[Usage Guide](docs/USAGE_GUIDE.md)**.

---

## 🏗️ Project Structure

The repository is organized to maintain a clean separation of code, documentation, and assets.

```
CheckinEdu/
│
├── .github/                # GitHub Actions workflows
├── assets/                 # Images, logos, and UI resources
├── data/                   # Default location for student photos and attendance CSVs
├── docs/                   # Project documentation (Usage Guide, etc.)
├── src/
│   ├── core/               # Model: Business logic and CV engine
│   ├── ui/                 # View & ViewModel: UI components and application state
│   └── utils/              # Helper functions and utilities
│
├── .env.example            # Example environment file
├── .gitignore              # Files to be ignored by Git
├── LICENSE                 # Project license file
├── main.py                 # Main entry point for the application
└── requirements.txt        # Python package dependencies
```

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  **Fork** the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a **Pull Request**

Please refer to the [Contributing Guidelines](CONTRIBUTING.md) for more details.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📞 Contact

Your Name - [@YourTwitterHandle](https://twitter.com/yourtwitterhandle) - your.email@example.com

Project Link: [https://github.com/hei1sme/CheckinEdu](https://github.com/hei1sme/CheckinEdu)

---

## Acknowledgements

*   [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
*   [OpenCV](https://opencv.org/)
*   [FPT University](https://fpt.edu.vn/) for the project inspiration.
*   [Shields.io](https://shields.io/) for the awesome badges.