# Nola API

This is a simple FastAPI application for nola tool.

## Installation

1. Clone the repository
2. Set up a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Use the following command to run the application:

```bash
uvicorn app.main:app --reload
```

## api docs
``` http
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```