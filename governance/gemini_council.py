import asyncio
import os
import uuid
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import ValidationError
from core.registry import AgentRegistry
from core.gemini_agent import GeminiAgent
from core.verdicts import AgentVerdict, VerdictType
from core.memory_store import MemoryStore
from governance.feedback_loop import FeedbackLoop
from core.event_bus import EventBus, EventType
from core.token_manager import TokenManager
from governance.adaptive_router import AdaptiveRouter
from governance.mediator import CivilizedMediator

class CouncilFailurePolicy(Enum):
    FAIL_OPEN = "fail_open"
    FAIL_CLOSED = "fail_closed"

class GeminiCouncil:
    """
    Async Council for multi-agent deliberation with Weighted Consensus, Veto Power, Adaptive Routing, and Mediator Resolution.
    Version: 6.0 (Integrated Hierarchical Council)
    """
    def __init__(self, registry: AgentRegistry = None, failure_policy: CouncilFailurePolicy = None, config: List[Dict] = None, memory_store: MemoryStore = None):
        self.registry = registry or AgentRegistry.create_default()
        self.memory_store = memory_store or MemoryStore()
        self.feedback_loop = FeedbackLoop(self.memory_store)
        self.agents: List[GeminiAgent] = []
        
        # Load Config or Default to Hierarchy
        self.agent_configs = {cfg['name']: cfg for cfg in (config or [])}
        
        self.event_bus = EventBus()
        self.token_manager = TokenManager()
        self.router = AdaptiveRouter(self.token_manager)
        self.mediator = CivilizedMediator(self.token_manager, self.event_bus)
        
        if failure_policy:
            self.failure_policy = failure_policy
        else:
            is_prod = os.environ.get("GEMINI_ENV") == "production"
            self.failure_policy = CouncilFailurePolicy.FAIL_CLOSED if is_prod else CouncilFailurePolicy.FAIL_OPEN

        self.council_timeout = 60

    async def deliberate(self, code: str, context: str, language: str = "python", complexity: int = 3) -> Dict[str, Any]:
        """
        Runs agents, validates verdicts, and calculates consensus.
        """
        session_id = str(uuid.uuid4())
        
        # 1. Route Task
        route = await self.router.route_task(f"{context} {code[:50]}", complexity)
        self.event_bus.publish(EventType.AGENT_ACTION, {
            "session_id": session_id,
            "agent": "Router",
            "action": "route_task",
            "target": f"{route.primary_provider}/{route.model}"
        })
        
        self.event_bus.publish(EventType.DELIBERATION_START, {"session_id": session_id, "code_hash": hash(code)})

        try:
            constraints = self.memory_store.get_active_constraints(language=language)
            
            async with asyncio.timeout(self.council_timeout):
                # 2. Run Agents
                raw_results = await self._run_agents(code, context, constraints, session_id, route)
                
                # 3. Calculate Consensus
                consensus = self._calculate_consensus(raw_results)
                
                # 4. Check for Deadlock (Score 0.4 - 0.6)
                if 0.4 <= consensus["confidence"] <= 0.6:
                    self.event_bus.publish(EventType.ERROR, {"session_id": session_id, "error": "DEADLOCK DETECTED - Spawning Mediator"})
                    
                    deadlock_data = {
                        "situation": "Council Consensus Weak",
                        "conflicting_perspectives": str(raw_results),
                        "active_constraints": constraints,
                        "task_context": context
                    }
                    
                    mediation = await self.mediator.attempt_resolution(deadlock_data, session_id)
                    consensus["mediation"] = mediation
                    
                    if mediation["action"] == "APPLY_RESOLUTION":
                        consensus["decision"] = "PASS" if mediation["resolution"]["verdict"] == "COMPROMISE" else "FAIL"
                        consensus["reason"] += f" [MEDIATED: {mediation['resolution']['rewritten_instructions']}]"

                self.event_bus.publish(EventType.CONSENSUS_REACHED, {"session_id": session_id, "consensus": consensus})
                
            self.event_bus.publish(EventType.DELIBERATION_END, {"session_id": session_id, "status": "success"})
            return {
                "session_id": session_id,
                "consensus": consensus,
                "agent_reviews": raw_results,
                "route": route,
                "code": code
            }

        except asyncio.TimeoutError:
            self.event_bus.publish(EventType.ERROR, {"session_id": session_id, "error": "timeout"})
            return self._handle_failure("Council Deliberation Timed Out")
        except Exception as e:
            self.event_bus.publish(EventType.ERROR, {"session_id": session_id, "error": str(e)})
            return self._handle_failure(str(e))

    async def record_outcome(self, verdict: Dict, outcome: str, details: Dict):
        """Bridge to the FeedbackLoop for institutional learning."""
        await self.feedback_loop.record_outcome(verdict, outcome, details)

    async def _run_agents(self, code: str, context: str, constraints: List[Any], session_id: str, route: Any) -> Dict[str, Any]:
        """Execute agents and parse/validate their verdicts."""
        tasks = {}
        
        if not self.agents:
            if not self.agent_configs:
                self.agent_configs = {
                    "LeadArchitect": {"weight": 3.0, "veto_power": False, "role": "Architect"},
                    "AdversarialValidator": {"weight": 1.0, "veto_power": True, "role": "Validator"}
                }
            
            for name in self.agent_configs:
                try:
                    agent = self.registry.create_agent(name)
                    self.agents.append(agent)
                except ValueError:
                    pass

        for i, agent in enumerate(self.agents):
            key = f"{agent.name}_{i}"
            routed_context = f"{context}\n[SYSTEM: Use Model {route.model} via {route.primary_provider}]"
            tasks[key] = asyncio.create_task(agent.query(code, routed_context, constraints=constraints))

        raw_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        processed_results = {}
        for key, result in zip(tasks.keys(), raw_results):
            agent_name = key.split('_')[0]
            if isinstance(result, Exception):
                self.event_bus.publish(EventType.ERROR, {"session_id": session_id, "agent": agent_name, "error": str(result)})
                processed_results[key] = {"verdict": VerdictType.ERROR, "confidence": 0.0, "reasoning": str(result)}
            elif isinstance(result, dict):
                try:
                    if "reasoning" not in result: result["reasoning"] = "No reasoning provided."
                    verdict_obj = AgentVerdict(**result)
                    payload = verdict_obj.model_dump()
                    processed_results[key] = payload
                    self.event_bus.publish(EventType.AGENT_VOTE, {"session_id": session_id, "agent": agent_name, "verdict": payload["verdict"], "confidence": payload["confidence"]})
                except ValidationError as e:
                    self.event_bus.publish(EventType.ERROR, {"session_id": session_id, "agent": agent_name, "error": "Schema Validation Failed"})
                    processed_results[key] = {"verdict": VerdictType.ERROR, "confidence": 0.0, "reasoning": f"Schema Validation Error: {e}"}
            else:
                processed_results[key] = result
        
        return processed_results

    def _calculate_consensus(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements Weighted Voting and Veto Logic.
        Gemini (3.0) vs Groq (1.0).
        """
        total_score = 0.0
        total_weight = 0.0
        blocking_agents = []
        
        for key, review in results.items():
            agent_name = key.split('_')[0]
            config = self.agent_configs.get(agent_name, {"weight": 1.0, "veto_power": False})
            
            verdict = review.get("verdict")
            confidence = review.get("confidence", 0.0)
            weight = config.get("weight", 1.0)
            veto = config.get("veto_power", False)

            if veto and verdict == VerdictType.FAIL:
                blocking_agents.append(agent_name)
            
            score_map = {VerdictType.PASS: 1.0, VerdictType.WARN: 0.5, VerdictType.FAIL: 0.0, VerdictType.ERROR: 0.0}
            total_score += score_map.get(verdict, 0.0) * confidence * weight
            total_weight += weight

        if blocking_agents:
            return {"decision": "FAIL", "confidence": 1.0, "reason": f"Blocked by Veto: {', '.join(blocking_agents)}"}

        if total_weight == 0:
            return {"decision": "FAIL", "confidence": 0.0, "reason": "No valid votes cast"}
            
        final_score = total_score / total_weight
        
        if final_score >= 0.7: decision = "PASS"
        elif final_score >= 0.4: decision = "WARN"
        else: decision = "FAIL"

        return {"decision": decision, "confidence": round(final_score, 2), "reason": f"Weighted Score: {final_score:.2f}"}

    def _handle_failure(self, error_msg: str) -> Dict[str, Any]:
        if self.failure_policy == CouncilFailurePolicy.FAIL_CLOSED:
            raise Exception(f"Council Failure (CLOSED): {error_msg}")
        else:
            return {"consensus": {"decision": "WARN", "confidence": 0.0, "reason": f"Council Failed: {error_msg}"}, "fallback": True}