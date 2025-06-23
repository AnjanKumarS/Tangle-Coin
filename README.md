# TangleCoinD

TangleCoinD is a project designed to demonstrate a cryptocurrency system based on a Directed Acyclic Graph (DAG) structure, inspired by the Tangle protocol. It features a backend server and a frontend dashboard for visualizing and interacting with the DAG-based ledger.

## Features
- DAG-based cryptocurrency ledger
- Backend API for transaction management
- Frontend dashboard for visualization and interaction
- Simple database integration

## Project Structure
```
TangleCoinD/
  backend/
    app.py            # Flask backend server
    tanglecoind.db    # SQLite database for storing transactions
  frontend/
    dag.html          # DAG visualization page
    dashboard.html    # Dashboard interface
    index.html        # Landing page
  README.md           # Project documentation
  venv/               # Python virtual environment
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### 1. Clone the repository
```bash
git clone <repo-url>
cd TangleCoinD
```

### 2. Set up a virtual environment (optional but recommended)
```bash
python -m venv venv
# Activate the virtual environment:
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install flask flask-cors
```

### 4. Run the backend server
```bash
cd backend
python app.py
```

### 5. Open the frontend
Open the HTML files in the `frontend/` directory (e.g., `dashboard.html`) in your web browser.

## Usage
- Use the dashboard to view and interact with the DAG-based ledger.
- The backend provides API endpoints for submitting and querying transactions.

## License
This project is for educational purposes.