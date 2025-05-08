#!/bin/bash

# Check if pip3 is already installed
if command -v pip3 &> /dev/null
then
    echo "pip3 is already installed."
else
    echo "pip3 is not installed. Installing..."
    # Download get-pip.py
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    
    # Install pip3
    python3 get-pip.py
    
    # Remove get-pip.py
    rm get-pip.py
    
    echo "pip3 has been installed."
fi