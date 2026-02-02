#!/bin/bash

# Activation script for HRMS Backend

cd /Users/ayushmaheshwari/Desktop/Quess_Corp/Backend

# Activate virtual environment
source venv/bin/activate

echo "✓ Virtual environment activated"
echo "✓ To run the server, execute:"
echo ""
echo "  python3 -m uvicorn HrmsBackend.main:app --reload --port 8000"
echo ""
echo "✓ The API will be available at http://127.0.0.1:8000"
echo "✓ Interactive API docs: http://127.0.0.1:8000/docs"
