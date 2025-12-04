# Forecasta Lead Analysis Dashboard Launcher
# Quick script to start the web dashboard

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "FORECASTA LEAD ANALYSIS DASHBOARD" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Set Python path
$env:PYTHONPATH = $PSScriptRoot

# Check if Flask is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import flask" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Flask not found. Installing..." -ForegroundColor Yellow
        pip install flask
    } else {
        Write-Host "✓ Flask installed" -ForegroundColor Green
    }
} catch {
    Write-Host "Installing Flask..." -ForegroundColor Yellow
    pip install flask
}

Write-Host ""
Write-Host "Starting dashboard server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 Leads directory: output/leads" -ForegroundColor Gray
Write-Host "🌐 Dashboard URL: " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "✓ Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Run the dashboard
python dashboard/leads_app.py
