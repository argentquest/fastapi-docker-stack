# Frontend Gemini: Project Documentation

This document outlines the structure and implementation of the NiceGUI-based frontend created for the InkAndQuill V2 POC application.

## 1. Summary of Work

A new frontend was created using the [NiceGUI](https://nicegui.io/) Python framework to provide a user interface for interacting with the application's FastAPI endpoints.

The key changes include:
- A new `frontendgemini` directory was added to house all frontend-related code.
- The main application file (`app/main.py`) was modified to serve the NiceGUI frontend alongside the existing API.
- The project's dependencies (`pyproject.toml`) were updated to include the `nicegui` library.

## 2. Directory Structure: `frontendgemini/`

The `frontendgemini` directory contains all the code for the user interface.

```
frontendgemini/
├── __init__.py
└── ui.py
```

### `__init__.py`

This is an empty file that serves a crucial purpose: it tells the Python interpreter to treat the `frontendgemini` directory as a package. This allows us to import its contents (like the UI code) from other parts of the application, such as `app/main.py`.

### `ui.py`

This is the core file for the frontend. It contains all the NiceGUI code to define the pages, components, and logic for the user interface.

The file is structured as follows:

- **Helper Functions for API Calls:**
  - A set of `async` functions (`run_ai_test_api`, `run_health_check_api`, etc.) that use the `httpx` library to communicate with the backend FastAPI endpoints. This separates the API communication logic from the UI layout code.

- **UI Page Definitions:**
  - **`render_header()`:** A function that creates a consistent navigation header for all pages.
  - **`@ui.page('/')` (AI Test Page):** This is the main landing page. It provides a user interface for the `/ai-test` endpoint, with text areas for inputs, a submit button, and a card to display the detailed results.
  - **`@ui.page('/tools')` (Tools Page):** This is a secondary page that provides a UI for the other utility endpoints. It includes:
    - A "Health Check" section to view the status of all backend services.
    - A "Simple AI Prompts" section to send requests to the various OpenRouter and Google AI models.

This structure keeps the frontend code organized and modular, making it easier to understand and maintain.
