# RESTORE_V5.2.ps1
# Industry standard rollback script to restore the stable Gemini v5.2 Kernel.

Write-Host "Starting Rollback to v5.2 Stable..." -ForegroundColor Yellow

# Ensure we are in the right directory
if (-not (Test-Path .git)) {
    Write-Error "Error: No git repository found in the current directory."
    exit 1
}

# Force checkout of the stable tag
git checkout main
git reset --hard v5.2-stable

Write-Host "SUCCESS: Restored to v5.2 stable." -ForegroundColor Green
Write-Host "Feature branch 'feature/v6.0-multi-agent' is still available for inspection." -ForegroundColor Cyan
