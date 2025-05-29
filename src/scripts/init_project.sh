PROJECT_NAME=$(grep -Po '^name = "\K[^"]*' pyproject.toml)

# Create virtual environment
virtualenv ./.venv --prompt="($PROJECT_NAME)"

# Install dependencies
source .venv/bin/activate && pip install -r requirements.txt
