# Adaptive Agent Kernel (AAK) v5.2

**A persistent, self-correcting operating system for LLMs running in local environments.**

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Platform](https://img.shields.io/badge/platform-PowerShell-blue) ![Author](https://img.shields.io/badge/author-Adeel%20Ahmad-orange)

## 🧠 The Philosophy
Most AI interactions are **stateless**: every new chat is a reset button. You repeat your preferences, your hardware limits, and your past corrections.

The **Adaptive Agent Kernel (AAK)** changes this by introducing a **Persistent Cognitive Layer**. It forces the AI to check a local "Long-Term Memory" before acting, enabling it to:
1.  **Remember Failures:** Uses a "Reflexion Loop" to log mistakes as negative constraints.
2.  **Enforce Safety:** Separates "Hard Invariants" (Safety) from "Soft Policies" (Preferences).
3.  **Maintain State:** Tracks project status via a structured `WORKLOG.md`.

## 🚀 Quick Start

### Prerequisites
* Windows / PowerShell 7+
* Git

### Installation
1.  Download `INSTALL.ps1`.
2.  Run the script:
    ```powershell
    .\INSTALL.ps1
    ```
3.  The kernel will be installed to `~/.gemini/GEMINI_GLOBAL.md`.

## ⚡ Core Algorithms

### 1. The Reflexion Loop (Self-Correction)
Instead of infinite retry loops, the kernel enforces a strict 3-strike termination rule:
> *Error -> Analyze -> Log Constraint -> Retry -> (Stop at 3)*

### 2. Strategy Selection Matrix
The kernel dynamically shifts strategies based on task confidence:
* **High Confidence:** Direct Execution.
* **Low Confidence:** Chain of Verification (Draft -> Critique -> Finalize).

## ⚖️ Disclaimer & Liability
**This software is provided "as is", without warranty of any kind.**

By using the Adaptive Agent Kernel (AAK), you acknowledge that:
1.  **Experimental Nature:** This system modifies core agent behaviors and file system operations.
2.  **No Liability:** In no event shall the author (**Adeel Ahmad**) be liable for any claim, damages, data loss, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.
3.  **User Responsibility:** You are solely responsible for reviewing code execution and securing your environment.

**Use at your own risk.**

## 👤 Author & Support

Created and Maintained by **Adeel Ahmad**.

* **Connect on LinkedIn:** [Adeel Ahmad](https://www.linkedin.com/in/engradeelahmad)

---
*Copyright © 2026 Adeel Ahmad. All Rights Reserved.*