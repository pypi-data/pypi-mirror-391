#!/bin/bash

# --- 1. SETUP ---
echo "Creating virtual environment..."
python3 -m venv venv

echo "Upgrading pip and installing required Python packages..."
# Run pip using the full path before activation
venv/bin/pip install --upgrade pip
venv/bin/pip install readchar tabulate

# --- 2. ACTIVATION FUNCTION ---
# This function handles the actual activation command
activate_venv() {
    # The 'source' command is executed here
    source venv/bin/activate
    echo -e "\nSetup completed successfully! Virtual environment is now **active**."
}

# --- 3. INSTRUCTION ---
echo -e "\n======================================================="
echo -e "Setup complete. To activate the environment, run:"
echo -e "\033[1;32msource setup.sh activate\033[0m"
echo -e "======================================================="

# --- 4. CONDITIONAL EXECUTION (Automation) ---
# If the user runs the script using 'source setup.sh activate', 
# the second argument ($2) will be 'activate', triggering the function.
if [ "$1" == "activate" ]; then
    activate_venv
fi