# Simple PowerShell startup script
Write-Host "Starting Downloads Monitor..." -ForegroundColor Green

# Activate virtual environment
& ".venv\Scripts\Activate.ps1"

# Run the program
python app.py

Write-Host "`nProgram completed, press Enter to exit..." -ForegroundColor Yellow
Read-Host
