# Gemini Adaptive Agent Kernel (AAK) v6.0

**The "Civilization" Update: A Persistent, Self-Correcting Hierarchical Council for Autonomous AI.**

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Platform](https://img.shields.io/badge/platform-PowerShell-blue) ![Architecture](https://img.shields.io/badge/architecture-Hierarchical%20Council-green) ![Status](https://img.shields.io/badge/status-Production%20Ready-success)

## ðŸŒ  The Vision: From Agents to Civilization
Most AI agents are lonely, hallucinating singletons. **Gemini v6.0** introduces a **Hierarchical Council** structure that mimics human engineering organizations to ensure accuracy, safety, and resilience.

It solves the "Single Point of Failure" problem by distributing cognition across specialized roles and models.

## ðŸ›ï¸ Core Architecture: The Integrated Hierarchical Council

### 1. The Authority (Decision Logic)
A weighted governance model that prioritizes accuracy over consensus.
*   **Lead Architect (Gemini Pro):** **3.0 Weight**. Handles synthesis, architecture, and complex logic. The "Senior Principal Engineer".
*   **Adversarial Validator (Llama 3 via Groq):** **1.0 Weight**. Handles speed checks, security scanning, and adversarial testing. The "QA/Security Engineer".
*   **Routing:** A **Complexity Router** automatically assigns trivial tasks (formatting) to `Gemini Flash` and complex tasks to `Gemini Pro`.

### 2. The Observer (Flight Recorder)
A read-only TUI dashboard that makes AI reasoning visible in real-time.
*   **Loop Detection:** Automatically halts execution if an agent gets stuck (3x repetition).
*   **Fuel Gauge:** Tracks API quotas (Groq RPM) and Budget (Gemini $) to prevent outages.
*   **Event Bus:** Zero-cost fire-and-forget messaging system.

### 3. The Civilization (Self-Healing)
*   **Deadlock Resolution:** If the Council deadlocks (Consensus Score 0.4-0.6), a **Mediator Agent** is spawned.
*   **Chain-of-Verification:** The Mediator analyzes the conflict, reviews evidence, and rewrites instructions to "unstick" the team.
*   **Trust Floor:** Security validation is *never* delegated to weak models (< 70B parameters).

## ðŸš€ Quick Start

### Prerequisites
* Python 3.12+
* `groq` and `google-generativeai` API keys.

### Installation
```powershell
./INSTALL.ps1
```

### Running the Kernel
```powershell
python run.py
```

### Launching the Dashboard (Flight Recorder)
Open a new terminal and run:
```powershell
python dashboard/app.py
```

## ðŸ› ï¸ Technology Stack
*   **Kernel:** Python 3.12 (AsyncIO)
*   **Dashboard:** Textual (TUI)
*   **Logic:** Gemini 1.5 Pro, Llama 3.3 70B, Mixtral 8x7B
*   **Governance:** Pydantic (Schema Validation)

## ðŸ“œ License
MIT License. See `LICENSE` for details.
