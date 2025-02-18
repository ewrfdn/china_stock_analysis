$envName = "stock_scraper"

# Check if conda is installed
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Host "conda could not be found. Please install Anaconda or Miniconda first."
    exit 1
}

# Check if the environment already exists
$envExists = conda env list | Select-String -Pattern $envName
if ($envExists) {
    Write-Host "Environment $envName already exists. Activating..."
}
else {
    Write-Host "Creating new conda environment: $envName"
    conda create --name $envName python=3.12 -y
}

# Activate the environment
conda activate $envName

# Install required packages
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
}

Write-Host "Conda environment setup complete."