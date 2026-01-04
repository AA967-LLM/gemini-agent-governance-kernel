# AGENT UPGRADE PLAN: The "Council of AI" Architecture
**Objective:** Evolve the Gemini CLI from a single-model agent into a Multi-Model Orchestrator with "One-Prompt" capability.

## 1. THE ARCHITECTURE
The goal is to eliminate "Single Point of Failure" logic by introducing a consensus mechanism using free resources.

### The "Council" Members
| Role | Model / Provider | Method | Cost | Specialization |
|------|-----------------|--------|------|----------------|
| **The Architect** | **Gemini (Current)** | API | Free | Context management, file I/O, planning, user interaction. |
| **The Critic** | **Llama 3 (via Groq)** | Cloud API | Free | High-speed logic checking, architectural review, error spotting. |
| **The Specialist** | **DeepSeek Coder** | **Ollama (Local)** | Free | Deep algorithmic verification, null-safety checks, pure code generation. |

## 2. WORKFLOW: The "Consensus Loop"

Instead of `Plan -> Code`, the new workflow is:

1.  **Draft:** Gemini generates a code solution.
2.  **Review:** Gemini passes the code to the `consensus_engine.py` script.
3.  **Vote:**
    *   **Groq:** Checks for high-level logic flaws.
    *   **Ollama:** Checks for syntax/compilation risks.
4.  **Refine:** If either voter detects high risk, Gemini self-corrects.
5.  **Commit:** Only "Ratified" code is written to the file system.

## 3. IMPLEMENTATION STEPS

### Phase 1: Infrastructure Setup (User Action)
- [ ] **Install Ollama:** Download from [ollama.com](https://ollama.com).
- [ ] **Pull Models:** Run `ollama pull deepseek-coder:6.7b` (or larger depending on RAM).
- [ ] **Get Groq Key:** Sign up at [console.groq.com](https://console.groq.com) and generate a free API key.
- [ ] **Configure Environment:** Add keys to a secure `.env` file (e.g., `GROQ_API_KEY=...`).

### Phase 2: The Consensus Engine (Agent Action)
- [ ] **Create `scripts/consensus.py`:**
    - Python script to handle API requests to Groq and Localhost:11434.
    - JSON-structured input/output for machine parsing.
- [ ] **Create `scripts/ask_council.py`:**
    - CLI wrapper for easier agent interaction.
    - Usage: `python ask_council.py --snippet "fun main() { ... }" --focus "safety"`

### Phase 3: Governance Integration
- [ ] **Update `AI_AGENT_QUICKREF.md`:** Add a rule: *"Critical logic changes MUST pass Consensus Check."*
- [ ] **Update Agent Capabilities:** Teach the agent (me) to call these scripts before modifying sensitive files (`LocationRepository`, `SensorRepository`).

## 4. IMMEDIATE NEXT ACTIONS
1.  **User:** Confirm installation of Ollama (optional but recommended) and Groq Key.
2.  **Agent:** Scaffold the `scripts/` directory and write the connection test scripts.

---
**Status:** Drafted
**Author:** Gemini CLI
**Date:** 2026-01-04
