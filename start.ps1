# Enhanced PowerShell startup script for Downloads Monitor
param(
    [string]$Mode = "once",
    [int]$Interval = 60,
    [switch]$NoExt,
    [switch]$Info,
    [switch]$ExtOnly,
    [string]$LogLevel = "INFO"
)

Write-Host "Downloads Monitor - Enhanced Startup Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and add it to PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    & ".venv\Scripts\Activate.ps1"
    Write-Host "Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "Failed to activate virtual environment: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies if needed (dev dependencies are optional)
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Build command line arguments
$args = @()
switch ($Mode) {
    "continuous" { 
        $args += "-c", $Interval 
        Write-Host "Running in continuous mode with $Interval second intervals" -ForegroundColor Green
    }
    "info" { 
        $args += "--info"
        Write-Host "Displaying system information" -ForegroundColor Green
    }
    "ext-only" { 
        $args += "--ext-only"
        Write-Host "Running extensions only" -ForegroundColor Green
    }
    default { 
        Write-Host "Running single monitoring cycle" -ForegroundColor Green
    }
}

if ($NoExt) {
    $args += "--no-ext"
    Write-Host "Extensions disabled" -ForegroundColor Yellow
}

$args += "--log-level", $LogLevel

# Run the program
Write-Host "`nStarting Downloads Monitor..." -ForegroundColor Green
Write-Host "Command: python app.py $($args -join ' ')" -ForegroundColor Gray
Write-Host "" # Empty line

python app.py @args
$exitCode = $LASTEXITCODE

# Show completion status
Write-Host "" # Empty line
if ($exitCode -eq 0) {
    Write-Host "Program completed successfully" -ForegroundColor Green
} else {
    Write-Host "Program exited with error code: $exitCode" -ForegroundColor Red
}

Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
