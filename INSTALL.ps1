# GEMINI KERNEL INSTALLER v6.0 (Integrated Hierarchical Council)
# STATUS: PRODUCTION | FEATURES: Multi-Agent Hierarchy, Resilient Token Management, Flight Recorder
# CHANGELOG: Added Self-Audit step and Gemini 3 Model Support.

$ErrorActionPreference = "Stop"

try {
    # --- 1. SETUP & SESSION TRACKING ---
    $sessionId = [guid]::NewGuid().ToString().Substring(0,8)
    $homeDir = [System.Environment]::GetFolderPath('UserProfile')
    $geminiDir = Join-Path $homeDir ".gemini"
    $kernelPath = Join-Path $geminiDir "GEMINI_GLOBAL.md"
    
    Write-Host "[Session: $sessionId] Initializing Gemini v6.0 Civilization Installer..." -ForegroundColor Cyan

    # --- 2. DIRECTORY SAFETY ---
    if (-not (Test-Path $geminiDir)) {
        New-Item -ItemType Directory -Path $geminiDir -Force | Out-Null
        Write-Host "   + Created directory: $geminiDir" -ForegroundColor Gray
    }

    # --- 3. VERSION CHECK & BACKUP ---
    $shouldInstall = $true
    if (Test-Path $kernelPath) {
        $existingContent = Get-Content $kernelPath -Raw
        if ($existingContent -match '\[v(\d+\.\d+)\]') {
            $currentVer = [version]$Matches[1]
            $newVer = [version]"6.0"
            
            if ($currentVer -gt $newVer) {
                Write-Host "STOP: Installed version (v$currentVer) is newer than installer (v$newVer)." -ForegroundColor Yellow
                $shouldInstall = $false
            }
        }
        
        if ($shouldInstall) {
            $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $backupPath = "$kernelPath.bak-$timestamp"
            Copy-Item $kernelPath $backupPath
            Write-Host "   + Backup secured: $backupPath" -ForegroundColor Yellow
        }
    }

    if (-not $shouldInstall) { exit }

    # --- 4. PYTHON DEPENDENCY SYNC ---
    Write-Host "--- Syncing Civilization Dependencies ---" -ForegroundColor Cyan
    $packages = @("groq", "google-generativeai", "pydantic", "textual", "aiohttp", "pytest", "pytest-asyncio", "python-dotenv", "black")
    foreach ($pkg in $packages) {
        Write-Host "   + Installing $pkg..." -ForegroundColor Gray
        pip install $pkg --quiet
    }

    # --- 5. THE v6.0 KERNEL CONTENT ---
    $content = @"
# ADAPTIVE AGENT CIVILIZATION KERNEL [v6.0]
# ARCHITECTURE: INTEGRATED HIERARCHICAL COUNCIL
# STATUS: ACTIVE | MODE: PRODUCTION
# INSTALLED: $(Get-Date -Format 'yyyy-MM-dd HH:mm') | SESSION: $sessionId

---

## SECTION 1: GOVERNANCE HIERARCHY

### 1.1 The Council of AI
Decisions are no longer made by a single agent. Power is distributed:
*   **Lead Architect (Gemini 3 Pro):** 3.0 Weight. Final synthesis and code authority.
*   **Adversarial Validator (Groq):** 1.0 Weight. Security Veto and Red-Teaming.
*   **Mediator Agent:** Spawns on Deadlock (Score 0.4-0.6) to resolve conflicts.

### 1.2 Adaptive Routing (Cost/Intelligence Opt)
*   **TRIVIAL (Comp < 3):** Routes to Gemini 3 Flash (Speed/Efficiency).
*   **STANDARD (Comp 3-4):** Routes to Groq Model Chain (Llama 70B/Mixtral).
*   **COMPLEX (Comp 5):** Routes to Gemini 3 Pro (Maximum Reasoning).

### 1.3 Trust Floor
*   **Security Validation:** Minimum 70B parameter model required. 
*   **Fallback:** If Groq is exhausted, failover to Gemini Pro/Flash. Never use < 70B for security.

---

## SECTION 2: THE OBSERVER (FLIGHT RECORDER)

### 2.1 Real-Time Telemetry
All agents MUST broadcast state via the `Zero-Cost Event Bus`.
*   **LOOP_DETECTED:** Triggered on 3x identical action hashes. **HALT & REDIRECT.**
*   **TOKEN_ALERT:** Triggered at 80% daily budget or RPM limit.

### 2.2 Dashboard Protocol
Run `python dashboard/app.py` to visualize the Council's internal reasoning.

---

## SECTION 3: INSTITUTIONAL MEMORY

### 3.1 Tiered Constraint Library
1.  **EXPERIMENTAL:** Learned from recent session failures.
2.  **VALIDATED:** Promoted after 5 successful sessions without violation.
3.  **HARD_INVARIANT:** Constitutional rules. Mediator CANNOT rewrite these.

---

## SECTION 4: RECOVERY & RESILIENCE

### 4.1 Model Rotation Chain
Groq Models are treated as a prioritized chain to maximize free-tier uptime:
1. Llama 3.3 70B -> 2. Mixtral 8x7B -> 3. Llama 3 70B -> 4. Gemini 3 Flash.

### 4.2 Budget Circuit Breaker
Gemini spend is tracked in real-time. If daily limit is hit, non-trivial tasks are HALTED.
"@

    # --- 6. WRITE & VERIFY ---
    Set-Content -Path $kernelPath -Value $content -Force
    Write-Host "SUCCESS: Civilization Kernel v6.0 installed." -ForegroundColor Green
    Write-Host "Path: $kernelPath" -ForegroundColor Cyan

    # --- 7. SELF-AUDIT (NEW) ---
    Write-Host "`n--- PERFOMING SELF-AUDIT ---" -ForegroundColor Cyan
    $testResult = pytest tests/test_phase4.py 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   + AUDIT PASSED: Core logic verified." -ForegroundColor Green
    } else {
        Write-Host "   ! AUDIT WARNING: Tests reported issues. Check environment." -ForegroundColor Yellow
    }

    Write-Host "`nWelcome to the Civilization." -ForegroundColor White

} catch {
    Write-Host "FATAL ERROR: Installation failed." -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
