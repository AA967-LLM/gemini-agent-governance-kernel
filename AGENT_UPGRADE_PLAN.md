# AGENT UPGRADE PLAN: The "Council of AI" Architecture (v6.0)
**Objective:** Evolve the Gemini CLI into a Multi-Model Orchestrator with "One-Prompt" capability.

## 1. THE ARCHITECTURE (Ratified 2026-01-04)
**Model:** Integrated Hierarchical Council.
**Philosophy:** Accuracy-First (Gemini Pro) + Diversity-for-Validation (Groq).

### The "Council" Members
| Role | Model / Provider | Method | Weight | Function |
|------|-----------------|--------|--------|----------|
| **Lead Architect** | **Gemini Pro** | API (Paid) | **3.0** | Synthesis, Architecture, Complex Logic. Final Authority. |
| **Adversarial Validator** | **Llama 3 (Groq)** | API (Free) | **1.0** | Speed Checks, Security Scanning, Edge Case Detection. Can VETO. |
| **Mediator** | **Gemini Pro** | API (Paid) | **N/A** | Spawns only on Deadlock. Rewrites prompts to unstick the Council. |

## 2. WORKFLOW: The "Hierarchical Loop"
1.  **Route:** `ComplexityRouter` assigns task. (Trivial -> Groq, Complex -> Gemini).
2.  **Draft:** Lead Architect (Gemini) generates solution.
3.  **Validate:** Adversarial Validator (Groq) tries to *break* the solution.
4.  **Consensus:** 
    - If Score > Threshold: **PASS**.
    - If Groq Veto (Security): **BLOCK**.
    - If Tie/Loop: **SPAWN MEDIATOR**.

## 3. IMPLEMENTATION STATUS

### Phase 4a: The Observer (Flight Recorder) - [COMPLETE]
- [x] **Event Bus:** Zero-cost messaging with `LoopDetector` (Incident #002 fix).
- [x] **Token Manager:** Proactive rate limiting for Groq and budget tracking for Gemini.
- [x] **Dashboard:** `textual` TUI for real-time monitoring (`dashboard/app.py`).

### Phase 4b: The Authority (Hierarchical Governance) - [NEXT]
- [ ] **Refactor Council:** Implement 3.0 vs 1.0 weighting in `governance/gemini_council.py`.
- [ ] **Complexity Router:** Create `governance/complexity.py` to route tasks.
- [ ] **Agent Config:** Update `core/gemini_agent.py` to support multi-provider logic.

### Phase 4c: The Civilization (Dynamic Scaling) - [PENDING]
- [ ] **Mediator Agent:** Implement deadlock resolution logic.
- [ ] **Dynamic Spawning:** Logic to spin up temporary agents.

## 4. IMMEDIATE NEXT ACTIONS
1.  **Refactor Council:** Update the voting logic to respect the new weights.
2.  **Implement Router:** Build the decision logic for task assignment.

---
**Status:** In Progress (Phase 4b)
**Author:** Gemini CLI (Ratified by Council)
**Date:** 2026-01-04