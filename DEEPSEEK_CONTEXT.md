# Gemini Agent Governance Kernel: Project "Civilization"
> **Context File for DeepSeek / Documentation Agents**
> *Status: v6.0 Production | Date: 2026-01-05*

## 1. Project Manifesto
**The Problem:** Standard AI agents are "lonely singletons"â€”prone to hallucination, unchecked errors, and infinite loops.
**The Solution:** A **Hierarchical Council** ("Civilization") where specialized agents govern each other using checks and balances, simulating a human engineering organization.

**Core Philosophy:**
1.  **Governance > Intelligence:** A smart model without controls is dangerous.
2.  **Hierarchy:** Not all agents are equal. "Architects" lead; "Validators" audit.
3.  **Adversarial Validation:** Security agents must have Veto power.
4.  **Self-Healing:** The system must detect deadlocks and loops, spawning "Mediators" to fix them autonomously.

---

## 2. High-Level Design (HLD)

### The Council Architecture
The system is split into **Governance** (Decision Making) and **Execution** (Raw Compute).

*   **The Authority (Governance Layer):**
    *   **Lead Architect (Gemini 3 Pro):** Weight 3.0. Handles complex logic and synthesis.
    *   **Adversarial Validator (Llama 3 70B via Groq):** Weight 1.0. Handles security and sanity checks. **Has VETO power.**
    *   **The Router:** Routes tasks based on complexity (Flash vs. Pro vs. Groq).
*   **The Civilization (Resilience Layer):**
    *   **Mediator Agent:** Spawns only when the Council deadlocks (Consensus Score 0.4-0.6).
    *   **Loop Detector:** Halts stuck agents.
*   **The Observer (Visibility Layer):**
    *   **Flight Recorder:** TUI Dashboard showing real-time thought processes.

### Routing Logic (Adaptive Router)
| Complexity | Model | Provider | Use Case |
| :--- | :--- | :--- | :--- |
| **1-2** | Gemini 3 Flash | Google | Formatting, Typos, Summaries |
| **3-4** | Llama 3 70B | Groq | Validation, Unit Tests, Security |
| **5** | Gemini 3 Pro | Google | Architecture, Complex Refactoring |

---

## 3. Low-Level Implementation (Code)

### A. The Council (`governance/gemini_council.py`)
*The central brain that manages voting and consensus.*

```python
class GeminiCouncil:
    async def deliberate(self, code: str, context: str, complexity: int = 3):
        # 1. Route Task
        route = await self.router.route_task(f"{context}", complexity)
        
        # 2. Run Agents (Parallel)
        raw_results = await self._run_agents(code, context, route)
        
        # 3. Consensus & Veto
        consensus = self._calculate_consensus(raw_results)
        
        # 4. Deadlock Resolution
        if 0.4 <= consensus["confidence"] <= 0.6:
            mediation = await self.mediator.attempt_resolution(raw_results)
            if mediation["action"] == "APPLY_RESOLUTION":
                consensus["decision"] = "PASS" # Compromise
                
        return consensus

    def _calculate_consensus(self, results):
        # Checks for Veto (Fail verdict from Validator)
        if blocking_agents:
             return {"decision": "FAIL", "reason": "Blocked by Veto"}
        # Calculates Weighted Score (Lead 3.0 vs Validator 1.0)
```

### B. The Adaptive Router (`governance/adaptive_router.py`)
*Optimizes cost and speed by selecting the right model.*

```python
class AdaptiveRouter:
    async def route_task(self, task: str, complexity: int):
        if complexity <= 2:
            return RoutingDecision(model="gemini-3-flash", provider="google")
        if complexity <= 4:
            return RoutingDecision(model="llama-3-70b", provider="groq")
        return RoutingDecision(model="gemini-3-pro", provider="google")
```

### C. The Mediator (`governance/mediator.py`)
*Resolves conflicts using Chain-of-Verification.*

```python
class CivilizedMediator:
    async def attempt_resolution(self, deadlock_data):
        # 1. Check Budget (Don't spawn infinitely)
        if not self.spawn_controller.can_spawn_mediator(): return {"action": "HALT"}
        
        # 2. Analyze Conflict (CoVe)
        analysis = await self._simulate_cove_analysis(deadlock_data)
        
        # 3. Propose Compromise
        return {"action": "APPLY_RESOLUTION", "resolution": "Rewritten Instructions..."}
```

---

## 4. Verification & Evidence

### Case Study: The "Hallucination Trap"
**Scenario:** The Lead Architect (Gemini 3 Pro) hallucinates that insecure SQL code is safe. The Validator (Groq) detects the error.
**Expectation:** Despite the Architect's 3x weight, the Validator's **Veto** must block the release.

**Live Proof (`scripts/demo_veto.py` Output):**
```text
>> AGENT REVIEW STARTED...
   [LeadArchitect] Reviewing... verdict: PASS (Confidence: 0.95)
   ... 'I see no issues with this code.' (HALLUCINATION)
   
   [SecurityValidator] Reviewing... verdict: FAIL (Confidence: 1.0)
   ... 'CRITICAL: SQL Injection vulnerability detected.' (REALITY)

--- FINAL VERDICT ---
DECISION: FAIL
REASON:   Blocked by Veto: SecurityValidator
```
*Status: VERIFIED (2026-01-05)*

### Test Suite (`tests/test_phase4.py`)
*   `test_adaptive_routing_trivial`: Confirms Flash is used for low complexity.
*   `test_adaptive_routing_complex`: Confirms Pro is used for high complexity.
*   `test_council_hierarchy_veto`: Confirms Veto logic overrides Weighted Score.
*   `test_mediator_deadlock_trigger`: Confirms Mediator spawns on 0.5 confidence.

---

## 5. Project History (The Journey)

*   **Phase 1: The Foundation**
    *   Replaced sync scripts with `asyncio`.
    *   Implemented Circuit Breakers.
*   **Phase 2: The Brain**
    *   Created the "Council" concept.
    *   Added Weighted Voting.
*   **Phase 3: The Memory**
    *   Added `memory.json` (Feedback Loop).
    *   Implemented "Reflexion" (Learning from mistakes).
*   **Phase 4: The Civilization (Current)**
    *   **Self-Healing:** Mediator Agents.
    *   **Visibility:** TUI Dashboard.
    *   **Efficiency:** Adaptive Routing (Groq/Flash).

---

## 6. Future Roadmap (Phase 5)
*   **Tool Use:** Allow agents to execute shell commands safely.
*   **RAG:** Vector memory for long-term project context.
*   **Skill Acquisition:** Agents writing their own tools.
