# Gemini Governance Kernel - Strategic Roadmap

This roadmap documents the strategic vision for the next evolution of the Gemini Kernel, based on findings from Incident #001 and industry standards for Memory Management (RAG/Summarization).

The primary objective is to transition the project from a "Text-Based POC" to a scalable, token-efficient "Enterprise Kernel."

## Execution Strategy
This roadmap is tentative and metric-driven. Implementation of subsequent phases depends on the outcomes of the observation phase (Phase 1). We will avoid premature optimization, ensuring that architectural complexity is introduced only when justified by data (e.g., token limits, performance degradation).

---

## Phase 1: Data Accumulation & Observation (Current v5.x)
**Goal:** Establish baselines to identify the "Bloat Point" (the moment memory size hurts performance).

### Metric Tracking
Implement a lightweight logger to track:
*   **Session Token Cost:** How many tokens does a standard session consume?
*   **Log Growth Rate:** How fast does `WORKLOG.md` grow (lines per incident)?
*   **Constraint Relevance:** How often are `[NEGATIVE_CONSTRAINTS]` actually triggered?

### The "Bloat" Trigger
Set a definitive threshold for moving to Phase 2 (e.g., "When `WORKLOG.md` exceeds 2,000 tokens" or "When the prompt includes >50 irrelevant lines").

---

## Phase 2: The "Archivist" Update (v6.0 - Text Optimization)
**Goal:** Implement "Hot" vs. "Cold" storage using simple text manipulation (No external databases yet).

### Memory Split Architecture
*   **`ACTIVE_CONTEXT.md` (Hot):** Contains only the current session, active Hard Invariants, and the last 5 relevant Negative Constraints.
*   **`ARCHIVE_HISTORY.md` (Cold):** A complete repository of all past sessions and resolved incidents. The AI does not read this by default.

### The "Summarization" Protocol
*   **Trigger:** When a session ends or `ACTIVE_CONTEXT` hits 500 lines.
*   **Action:** An automated prompt compresses the raw logs into a 3-bullet summary (e.g., "Tried X, Failed due to Y, Fixed with Z").
*   **Storage:** The raw logs move to Archive; the Summary stays in Active.

### Keyword Injection (Poor Man's RAG)
*   **Mechanism:** A script scans the User Prompt for keywords (e.g., "PowerShell", "Azure").
*   **Action:** It `grep`s the Archive for matching constraints and temporarily injects them into the Active Context.

---

## Phase 3: The "Librarian" Update (v7.0 - Semantic Intelligence)
**Goal:** Move from text files to Industry Standard Retrieval-Augmented Generation (RAG) to decouple Intelligence from Token Cost.

### Vectorization of Constraints
*   **Action:** Move `NEGATIVE_CONSTRAINTS` from Markdown into a simple JSON store or lightweight Vector DB (like ChromaDB local).
*   **Why:** To allow the kernel to store 10,000 rules but only feed the relevant 3 rules to the Agent at runtime.

### Semantic Search
*   **Upgrade:** Replace keyword matching (`grep`) with Semantic matching.
*   **Example:** If user asks for "Cleanup script," the system finds rules related to "Delete," "Remove," and "Safety" even if the exact words don't match.

### Episodic Memory Management
*   **Separation:** Separate Procedural Memory (How to do things/Rules) from Episodic Memory (What happened yesterday).
*   **Access:** Procedural Memory is always accessible via search. Episodic Memory is aggressively archived.

---

## Phase 4: Ecosystem & Collaboration (Governance Layer)
**Goal:** Standardize how these optimized memories are shared between environments (Dev → Test → Prod).

### Constraint Portability
*   **Feature:** Create command `i-export-constraints` to package learned lessons into a YAML file.
*   **Benefit:** Allows a "Junior" kernel to inherit the safety rules learned by a "Senior" kernel.

### The "Global" Safety List
*   **Repository:** Establish a shared repository of "Common Hallucinations" (e.g., the PowerShell UTF-8 issue) that all Kernels import by default.

---

## Summary of Strategy
1.  **Don't optimize prematurely:** Wait until the files actually get big (Phase 1).
2.  **Avoid complexity first:** Use file splitting and summarization (Phase 2) before adding databases.
3.  **Adopt Industry Standards:** Only move to Vector/RAG (Phase 3) when text search becomes too inefficient.
4.  **Keep Token Count Low:** By moving "Cold" data out of the Context Window, we ensure the agent stays smart and cheap, regardless of how long the project runs.
