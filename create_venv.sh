#!/bin/bash

ENV_NAME="stock_scraper"

# Check if conda is installed
if ! command -v conda &> /dev/null
then
    echo "conda could not be found. Please install Anaconda or Miniconda first."
    exit 1
fi

# Check if the environment already exists
if conda env list | grep -q "$ENV_NAME"; then
    echo "Environment $ENV_NAME already exists. Activating..."
else
    echo "Creating new conda environment: $ENV_NAME"
    conda create --name $ENV_NAME python=3.8 -y
fi

# Activate the environment
source activate $ENV_NAME

# Install required packages
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "Conda environment setup complete."
