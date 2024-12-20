# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Check dependencies ensure pip is updated
pip install --upgrade pip

# Saving to requirements.txt all installed dependencies
pip freeze > requirements.txt

# If requirements.txt is existing
pip install -r requirements.txt

# Run app
uvicorn main:app --reload