# SIST Student Result Portal

A Django-based student result management system for viewing academic performance, managing examination results, importing results from Excel, and generating downloadable PDF reports.

**Built with:** Python · Django · SQLite · HTML · CSS · JavaScript

[View Repository](https://github.com/kxrtik250/sist-result-portal)

## Overview

The SIST Student Result Portal provides separate workflows for students and staff to manage and access academic results. Students can view their own results and performance summaries, while authorized staff can manage student records and examination marks.

The project also includes Excel-based result imports, PDF report generation, and AI-assisted academic performance analysis.

## Features

- **Student authentication:** Student registration and login.
- **Student dashboard:** View personal examination results and filter results by semester.
- **Staff dashboard:** Search and manage student result records.
- **Result management:** Add, edit, and delete examination results.
- **Excel import:** Import examination results from `.xlsx` files.
- **PDF reports:** Download student result reports.
- **AI-assisted analysis:** Generate academic performance summaries and study suggestions.
- **Automated tests:** Tests for login redirects, student result isolation, and marks validation.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Django |
| Database | SQLite by default; database configuration supports `DATABASE_URL` |
| Frontend | HTML, CSS, JavaScript |
| Excel processing | openpyxl |
| PDF generation | ReportLab |
| AI integration | Google Gemini API |
| Testing | Django TestCase |

## Project Structure

```text
sist-result-portal/
├── manage.py
├── requirements.txt
├── student_result_system/
│   └── Django project configuration
└── results/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── ai_helper.py
    ├── tests.py
    └── templates and static files
```

## Getting Started

### Prerequisites

- Python installed on your system
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/kxrtik250/sist-result-portal.git
cd sist-result-portal
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the virtual environment's Python executable directly instead.

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Configure the Django secret key and other required settings through environment variables before running the application. If AI analysis is enabled, configure the Gemini API key securely as well.

Never commit real API keys, Django secret keys, passwords, or production environment files to GitHub.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the prompts to create the account.

### 7. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Run Tests

Run the project's Django tests with:

```bash
python manage.py test results
```

**Latest recorded test result:** 4 tests passed.

The tests cover student login, staff login, student-specific result visibility, and rejection of marks above 100.

## Security Notes

- Use fictional data when demonstrating the application publicly.
- Keep secret keys and API credentials outside source control.
- Restrict staff-only actions to authorized users.
- Validate uploaded Excel files and imported result values.
- Use production-specific security settings when deploying the application.

## Current Status

The project is maintained as a portfolio project. The source code is available on GitHub; a live hosted demo is not currently provided.

## Author

**Karthik Sriram S**

GitHub: [@kxrtik250](https://github.com/kxrtik250)
