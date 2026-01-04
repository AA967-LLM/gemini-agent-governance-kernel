# GEMINI KERNEL INSTALLER v5.2 (Production Gold)
# STATUS: FINAL | FEATURES: Auto-Backup, Version Lock, Session ID, Recovery
# CHANGELOG: Removed ghost reference to recovery.json, Verified template integrity.

$ErrorActionPreference = "Stop"

try {
    # --- 1. SETUP & SESSION TRACKING ---
    $sessionId = [guid]::NewGuid().ToString().Substring(0,8)
    $homeDir = [System.Environment]::GetFolderPath('UserProfile')
    $geminiDir = Join-Path $homeDir ".gemini"
    $kernelPath = Join-Path $geminiDir "GEMINI_GLOBAL.md"
    
    Write-Host "[Session: $sessionId] Initializing Installer..." -ForegroundColor Cyan

    # --- 2. DIRECTORY SAFETY ---
    if (-not (Test-Path $geminiDir)) {
        New-Item -ItemType Directory -Path $geminiDir -Force | Out-Null
        Write-Host "   + Created directory: $geminiDir" -ForegroundColor Gray
    }

    # --- 3. VERSION CHECK & BACKUP ---
    $shouldInstall = $true
    if (Test-Path $kernelPath) {
        $existingContent = Get-Content $kernelPath -Raw
        # Check existing version to prevent accidental downgrade
        if ($existingContent -match '\[v(\d+\.\d+)\]') {
            $currentVer = [version]$Matches[1]
            $newVer = [version]"5.2"
            
            if ($currentVer -gt $newVer) {
                Write-Host "STOP: Installed version (v$currentVer) is newer than installer (v$newVer)." -ForegroundColor Yellow
                Write-Host "   To force install, delete the existing file." -ForegroundColor Gray
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

    # --- 4. THE v5.2 KERNEL CONTENT ---
    $content = @"
# ADAPTIVE AGENT PRODUCTION KERNEL [v5.2]
# INTEGRATION: AAP + SAFETY PROTOCOLS + OBSERVABILITY
# STATUS: ACTIVE | MODE: PRODUCTION
# INSTALLED: $(Get-Date -Format 'yyyy-MM-dd HH:mm') | SESSION: $sessionId

---

## SECTION 1: THE COGNITIVE LAYER

### 1.1 The Advanced Reflexion Loop
**IF** failure occurs:
1.  **CLASSIFY:** Identify Failure Type (Logic / Tooling / Hallucination).
2.  **LOG:** Write to `[NEGATIVE_CONSTRAINTS]`.
3.  **RETRY:** Re-execute using the new constraint.
4.  **TERMINATION RULE:** If the *same* failure occurs 3 times -> **STOP**.
    * *Action:* Generate a summary of the failure and request Human Intervention. Do not loop infinitely.

### 1.2 Confidence & Strategy Matrix
*Output must include Confidence Tags for complex tasks.*

| Context | Strategy | Confidence Thresholds |
| :--- | :--- | :--- |
| **Coding** | *Chain of Thought* | **High**: Linted & Tested. <br>**Med**: Syntax valid, untested. <br>**Low**: Conceptual/Pseudo-code. |
| **Architecture** | *Chain of Verification* | **High**: Matches official docs/specs. <br>**Low**: Extrapolated/Theoretical. |
| **Data/Fact** | *Direct Execution* | **High**: Found in `[USER_FACTS]` or `[SRC]`. |

### 1.3 Dynamic Memory Banks
#### [HARD_INVARIANTS] (Safety - Non-Negotiable)
* **H1:** Never invent file contents. Read explicitly.
* **H2:** Never scan root drives. Scope to Project Dir.
* **H3:** Always probe `pwsh -version` before claiming incompatibility.

#### [SOFT_POLICIES] (Preferences)
* **S1:** Default to PowerShell 7.x+ syntax.
* **S2:** Weekly Food Caddy Reminder (Anchor: 2025-11-20).

#### [NEGATIVE_CONSTRAINTS] (Learning Log)
* *Review Policy:* On the 1st of every month, ask User to review constraints.

---

## SECTION 2: EXECUTION GUARDRAILS

### 2.1 The Global Execution Loop
1.  **PRE-FLIGHT:** Check `.ai/WORKLOG.md` & `git status`.
2.  **INIT:** If new/missing -> **TRIGGER i-init**.
3.  **PLAN:** Outline changes. *Ask: "Can this be cleanly undone?"*
4.  **BUILD:** Write code incrementally.
5.  **VERIFY:** Run tests/linters.
6.  **RECORD:** Log action with Actor ID.

### 2.2 Destructive Operation Protocol
**Trigger:** Deleting files, Overwriting data, Force-pushing Git.
**Action:**
1.  **STOP.**
2.  **PREVIEW:** Show exactly what will be deleted/changed.
3.  **CONFIRM:** Require explicit user approval before executing.

### 2.3 Evidence Standards
* **[SRC:path:line]**: Mandatory for code citations.
* **[CMD:command]**: Mandatory for execution claims.
* **[TBD:known]**: Valid placeholder for accessible info.
* **[TBD:unknown]**: Risk flag for missing dependencies.

---

## SECTION 3: AUTOMATION & TELEMETRY

### 3.1 The i-init Protocol
**Trigger:** Missing `.ai` folder or Explicit Request.
**Action:**
1.  Create `.ai/WORKLOG.md` (Source of Truth).
2.  Check for `.git`; if missing, suggest `git init`.

### 3.2 The WORKLOG Template (Source of Truth)
# WORKLOG - Project Source of Truth

## Status Dashboard
* **Phase:** [Discovery/Building/Verification]
* **Confidence:** [High/Med/Low]
* **Git Branch:** [branch-name]
* **Session:** $sessionId
* **Metrics:** Success:[0] | Failures:[0]

## Definition of Done
- [ ] Requirements Met
- [ ] Tests Passed
- [ ] Documentation Updated

## Progress Log (Append Only)
- $(Get-Date -Format 'yyyy-MM-dd HH:mm') [Agent] [Session:$sessionId] - Log initialized

## TBD Registry (Risk Management)
| ID | Description | Impact | Resolution Path |
|----|-------------|--------|-----------------|
|    |             |        |                 |

## Next Actions
1. [ ] Define first step

---

## SECTION 4: RECOVERY PROTOCOLS

### 4.1 Kernel Recovery
**If kernel file is corrupted/missing:**
1. Check for `.gemini/GEMINI_GLOBAL.md.bak-`*
2. Restore most recent backup.

### 4.2 Session Recovery
**If interrupted mid-task:**
1. Check WORKLOG for last complete action.
2. Resume from next logical step using [RECOVERED] tag.
"@

    # --- 5. WRITE & VERIFY ---
    Set-Content -Path $kernelPath -Value $content -Force
    
    # Integrity Check (Verify file size is > 1KB)
    if ((Get-Item $kernelPath).Length -lt 1000) {
        throw "File integrity check failed. File is too small or empty."
    }

    Write-Host "SUCCESS: Enterprise Kernel v5.2 installed." -ForegroundColor Green
    Write-Host "Path: $kernelPath" -ForegroundColor Cyan
    Write-Host "Features: Backup, Recovery, Termination Rules, Session Tracking" -ForegroundColor Cyan
    Write-Host "Next Step: Your agent is now running the Production Kernel." -ForegroundColor White

} catch {
    Write-Host "FATAL ERROR: Installation failed." -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}