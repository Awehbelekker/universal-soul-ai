"""
Collective Intelligence
=======================

Implements collective intelligence algorithms for synthesizing responses
from multiple AI agents and achieving consensus in multi-agent systems.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from ..config import OrchestrationConfig
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


class ConsensusMethod(Enum):
    """Methods for achieving consensus"""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_AVERAGE = "weighted_average"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    EXPERT_SELECTION = "expert_selection"
    HYBRID_SYNTHESIS = "hybrid_synthesis"


@dataclass
class ConsensusResult:
    """Result of consensus building process"""
    consensus_achieved: bool
    final_response: str
    confidence_score: float
    method_used: ConsensusMethod
    agreement_level: float
    participating_agents: List[str]
    synthesis_insights: Dict[str, Any]


class CollectiveIntelligence:
    """
    Collective Intelligence System
    
    Synthesizes responses from multiple AI agents using various consensus
    algorithms and collective intelligence techniques.
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.is_initialized = False
        
        # Consensus algorithms
        self.consensus_methods: Dict[str, Any] = {}
        self.synthesis_strategies: Dict[str, Any] = {}
        
        # Performance tracking
        self.consensus_history: List[Dict[str, Any]] = []
        self.method_performance: Dict[ConsensusMethod, Dict[str, float]] = {}
        
        # Learning state
        self.agent_reliability: Dict[str, float] = {}
        self.domain_expertise: Dict[str, Dict[str, float]] = {}
    
    async def initialize(self) -> None:
        """Initialize collective intelligence system"""
        try:
            logger.info("Initializing Collective Intelligence...")
            
            # Setup consensus methods
            await self._setup_consensus_methods()
            
            # Initialize synthesis strategies
            await self._setup_synthesis_strategies()
            
            # Load agent reliability data
            await self._load_agent_reliability()
            
            # Initialize performance tracking
            await self._initialize_performance_tracking()
            
            self.is_initialized = True
            logger.info("Collective Intelligence initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Collective Intelligence: {e}")
            raise ThinkMeshException(
                f"Collective Intelligence initialization failed: {e}",
                ErrorCode.ORCHESTRATION_INITIALIZATION_FAILED
            )
    
    async def synthesize_responses(self, individual_results: List[Dict[str, Any]],
                                 original_task: str, strategy: Any,
                                 require_consensus: bool = False) -> Dict[str, Any]:
        """Synthesize individual agent responses into collective response"""
        try:
            if not individual_results:
                raise ThinkMeshException(
                    "No individual results to synthesize",
                    ErrorCode.ORCHESTRATION_EXECUTION_FAILED
                )
            
            # Filter successful results
            successful_results = [
                result for result in individual_results 
                if result.get("success", False)
            ]
            
            if not successful_results:
                # Fallback to best available result
                successful_results = sorted(
                    individual_results, 
                    key=lambda x: x.get("confidence", 0.0), 
                    reverse=True
                )[:1]
            
            # Determine optimal consensus method
            consensus_method = await self._select_consensus_method(
                successful_results, original_task, require_consensus
            )
            
            # Apply consensus algorithm
            consensus_result = await self._apply_consensus_method(
                consensus_method, successful_results, original_task
            )
            
            # Generate collective insights
            insights = await self._generate_collective_insights(
                successful_results, consensus_result, original_task
            )
            
            # Update learning data
            await self._update_learning_data(
                successful_results, consensus_result, original_task
            )
            
            return {
                "final_response": consensus_result.final_response,
                "confidence_score": consensus_result.confidence_score,
                "consensus_achieved": consensus_result.consensus_achieved,
                "method_used": consensus_result.method_used.value,
                "agreement_level": consensus_result.agreement_level,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Response synthesis failed: {e}")
            raise
    
    async def _select_consensus_method(self, results: List[Dict[str, Any]],
                                     task: str, require_consensus: bool) -> ConsensusMethod:
        """Select optimal consensus method based on context"""
        # Analyze result characteristics
        confidence_variance = await self._calculate_confidence_variance(results)
        response_similarity = await self._calculate_response_similarity(results)
        agent_expertise = await self._assess_agent_expertise(results, task)
        
        # Select method based on characteristics
        if require_consensus and response_similarity < 0.5:
            # Low similarity, consensus required - use hybrid synthesis
            return ConsensusMethod.HYBRID_SYNTHESIS
        elif confidence_variance < 0.1 and response_similarity > 0.8:
            # High agreement - use confidence weighted
            return ConsensusMethod.CONFIDENCE_WEIGHTED
        elif len(results) == 1:
            # Single result - use expert selection
            return ConsensusMethod.EXPERT_SELECTION
        elif any(expertise > 0.8 for expertise in agent_expertise.values()):
            # High expertise available - use expert selection
            return ConsensusMethod.EXPERT_SELECTION
        else:
            # Default to weighted average
            return ConsensusMethod.WEIGHTED_AVERAGE
    
    async def _apply_consensus_method(self, method: ConsensusMethod,
                                    results: List[Dict[str, Any]],
                                    task: str) -> ConsensusResult:
        """Apply the selected consensus method"""
        if method == ConsensusMethod.MAJORITY_VOTE:
            return await self._majority_vote_consensus(results, task)
        elif method == ConsensusMethod.WEIGHTED_AVERAGE:
            return await self._weighted_average_consensus(results, task)
        elif method == ConsensusMethod.CONFIDENCE_WEIGHTED:
            return await self._confidence_weighted_consensus(results, task)
        elif method == ConsensusMethod.EXPERT_SELECTION:
            return await self._expert_selection_consensus(results, task)
        elif method == ConsensusMethod.HYBRID_SYNTHESIS:
            return await self._hybrid_synthesis_consensus(results, task)
        else:
            # Fallback to weighted average
            return await self._weighted_average_consensus(results, task)
    
    async def _majority_vote_consensus(self, results: List[Dict[str, Any]],
                                     task: str) -> ConsensusResult:
        """Implement majority vote consensus"""
        # Group similar responses
        response_groups = await self._group_similar_responses(results)
        
        # Find majority group
        majority_group = max(response_groups, key=len)
        
        # Select best response from majority group
        best_response = max(majority_group, key=lambda x: x.get("confidence", 0.0))
        
        agreement_level = len(majority_group) / len(results)
        consensus_achieved = agreement_level >= 0.5
        
        return ConsensusResult(
            consensus_achieved=consensus_achieved,
            final_response=best_response["response"],
            confidence_score=best_response.get("confidence", 0.7),
            method_used=ConsensusMethod.MAJORITY_VOTE,
            agreement_level=agreement_level,
            participating_agents=[r["agent_id"] for r in results],
            synthesis_insights={"majority_group_size": len(majority_group)}
        )
    
    async def _weighted_average_consensus(self, results: List[Dict[str, Any]],
                                        task: str) -> ConsensusResult:
        """Implement weighted average consensus"""
        # Calculate weights based on agent reliability and confidence
        weights = []
        for result in results:
            agent_id = result["agent_id"]
            confidence = result.get("confidence", 0.7)
            reliability = self.agent_reliability.get(agent_id, 0.7)
            
            weight = confidence * reliability
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(results)] * len(results)
        
        # Select response with highest weight
        best_index = weights.index(max(weights))
        best_response = results[best_index]
        
        # Calculate weighted confidence
        weighted_confidence = sum(
            w * r.get("confidence", 0.7) 
            for w, r in zip(weights, results)
        )
        
        # Calculate agreement level
        agreement_level = await self._calculate_response_similarity(results)
        
        return ConsensusResult(
            consensus_achieved=agreement_level > 0.6,
            final_response=best_response["response"],
            confidence_score=weighted_confidence,
            method_used=ConsensusMethod.WEIGHTED_AVERAGE,
            agreement_level=agreement_level,
            participating_agents=[r["agent_id"] for r in results],
            synthesis_insights={"weights": dict(zip([r["agent_id"] for r in results], weights))}
        )
    
    async def _confidence_weighted_consensus(self, results: List[Dict[str, Any]],
                                           task: str) -> ConsensusResult:
        """Implement confidence-weighted consensus"""
        # Sort by confidence
        sorted_results = sorted(results, key=lambda x: x.get("confidence", 0.0), reverse=True)
        
        # Use highest confidence response as base
        best_response = sorted_results[0]
        
        # Calculate agreement level
        agreement_level = await self._calculate_response_similarity(results)
        
        # Boost confidence if high agreement
        final_confidence = best_response.get("confidence", 0.7)
        if agreement_level > 0.8:
            final_confidence = min(final_confidence * 1.1, 1.0)
        
        return ConsensusResult(
            consensus_achieved=agreement_level > 0.7,
            final_response=best_response["response"],
            confidence_score=final_confidence,
            method_used=ConsensusMethod.CONFIDENCE_WEIGHTED,
            agreement_level=agreement_level,
            participating_agents=[r["agent_id"] for r in results],
            synthesis_insights={"confidence_ranking": [r["agent_id"] for r in sorted_results]}
        )
    
    async def _expert_selection_consensus(self, results: List[Dict[str, Any]],
                                        task: str) -> ConsensusResult:
        """Implement expert selection consensus"""
        # Assess agent expertise for this task
        expertise_scores = {}
        for result in results:
            agent_id = result["agent_id"]
            expertise = await self._calculate_agent_expertise(agent_id, task)
            expertise_scores[agent_id] = expertise
        
        # Select expert with highest score
        expert_agent = max(expertise_scores.keys(), key=lambda x: expertise_scores[x])
        expert_result = next(r for r in results if r["agent_id"] == expert_agent)
        
        # Calculate agreement level
        agreement_level = await self._calculate_response_similarity(results)
        
        return ConsensusResult(
            consensus_achieved=expertise_scores[expert_agent] > 0.8,
            final_response=expert_result["response"],
            confidence_score=expert_result.get("confidence", 0.7),
            method_used=ConsensusMethod.EXPERT_SELECTION,
            agreement_level=agreement_level,
            participating_agents=[r["agent_id"] for r in results],
            synthesis_insights={"expert_agent": expert_agent, "expertise_scores": expertise_scores}
        )
    
    async def _hybrid_synthesis_consensus(self, results: List[Dict[str, Any]],
                                        task: str) -> ConsensusResult:
        """Implement hybrid synthesis consensus"""
        # Combine multiple approaches
        
        # 1. Get expert opinion
        expert_result = await self._expert_selection_consensus(results, task)
        
        # 2. Get weighted average
        weighted_result = await self._weighted_average_consensus(results, task)
        
        # 3. Synthesize the two approaches
        if expert_result.confidence_score > weighted_result.confidence_score:
            final_response = expert_result.final_response
            final_confidence = expert_result.confidence_score
        else:
            final_response = weighted_result.final_response
            final_confidence = weighted_result.confidence_score
        
        # Calculate agreement level
        agreement_level = await self._calculate_response_similarity(results)
        
        return ConsensusResult(
            consensus_achieved=agreement_level > 0.6,
            final_response=final_response,
            confidence_score=final_confidence,
            method_used=ConsensusMethod.HYBRID_SYNTHESIS,
            agreement_level=agreement_level,
            participating_agents=[r["agent_id"] for r in results],
            synthesis_insights={
                "expert_confidence": expert_result.confidence_score,
                "weighted_confidence": weighted_result.confidence_score,
                "synthesis_method": "confidence_based_selection"
            }
        )
    
    async def _calculate_confidence_variance(self, results: List[Dict[str, Any]]) -> float:
        """Calculate variance in confidence scores"""
        confidences = [r.get("confidence", 0.7) for r in results]
        if len(confidences) <= 1:
            return 0.0
        
        mean_confidence = sum(confidences) / len(confidences)
        variance = sum((c - mean_confidence) ** 2 for c in confidences) / len(confidences)
        return variance
    
    async def _calculate_response_similarity(self, results: List[Dict[str, Any]]) -> float:
        """Calculate similarity between responses"""
        if len(results) <= 1:
            return 1.0
        
        # Simple similarity based on response length and common words
        responses = [r.get("response", "") for r in results]
        
        # Calculate average similarity
        similarities = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                similarity = await self._calculate_text_similarity(responses[i], responses[j])
                similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    async def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    async def _assess_agent_expertise(self, results: List[Dict[str, Any]], task: str) -> Dict[str, float]:
        """Assess agent expertise for the given task"""
        expertise = {}
        for result in results:
            agent_id = result["agent_id"]
            expertise[agent_id] = await self._calculate_agent_expertise(agent_id, task)
        
        return expertise
    
    async def _calculate_agent_expertise(self, agent_id: str, task: str) -> float:
        """Calculate agent expertise for a specific task"""
        # Base expertise from reliability
        base_expertise = self.agent_reliability.get(agent_id, 0.7)
        
        # Domain-specific expertise
        task_domain = await self._identify_task_domain(task)
        domain_expertise = self.domain_expertise.get(agent_id, {}).get(task_domain, 0.7)
        
        # Combine base and domain expertise
        return (base_expertise + domain_expertise) / 2
    
    async def _identify_task_domain(self, task: str) -> str:
        """Identify the domain of a task"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["analyze", "research", "study"]):
            return "analytical"
        elif any(word in task_lower for word in ["create", "design", "write"]):
            return "creative"
        elif any(word in task_lower for word in ["code", "program", "technical"]):
            return "technical"
        elif any(word in task_lower for word in ["solve", "fix", "troubleshoot"]):
            return "problem_solving"
        else:
            return "general"
    
    async def _group_similar_responses(self, results: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group similar responses together"""
        groups = []
        similarity_threshold = 0.7
        
        for result in results:
            placed = False
            for group in groups:
                # Check similarity with group representative (first item)
                similarity = await self._calculate_text_similarity(
                    result.get("response", ""), 
                    group[0].get("response", "")
                )
                if similarity >= similarity_threshold:
                    group.append(result)
                    placed = True
                    break
            
            if not placed:
                groups.append([result])
        
        return groups
    
    async def _generate_collective_insights(self, results: List[Dict[str, Any]],
                                          consensus_result: ConsensusResult,
                                          task: str) -> Dict[str, Any]:
        """Generate insights from collective intelligence process"""
        insights = {
            "total_agents": len(results),
            "successful_agents": len([r for r in results if r.get("success", False)]),
            "average_confidence": sum(r.get("confidence", 0.0) for r in results) / len(results),
            "consensus_method": consensus_result.method_used.value,
            "agreement_level": consensus_result.agreement_level,
            "response_diversity": 1.0 - consensus_result.agreement_level,
            "collective_confidence": consensus_result.confidence_score
        }
        
        # Add domain-specific insights
        task_domain = await self._identify_task_domain(task)
        insights["task_domain"] = task_domain
        
        # Add agent performance insights
        agent_performances = {}
        for result in results:
            agent_id = result["agent_id"]
            agent_performances[agent_id] = {
                "confidence": result.get("confidence", 0.0),
                "success": result.get("success", False),
                "response_length": len(result.get("response", ""))
            }
        insights["agent_performances"] = agent_performances
        
        return insights
    
    async def _update_learning_data(self, results: List[Dict[str, Any]],
                                  consensus_result: ConsensusResult, task: str) -> None:
        """Update learning data based on consensus results"""
        # Update agent reliability
        for result in results:
            agent_id = result["agent_id"]
            success = result.get("success", False)
            confidence = result.get("confidence", 0.0)
            
            # Update reliability using exponential moving average
            current_reliability = self.agent_reliability.get(agent_id, 0.7)
            performance_score = confidence if success else 0.0
            
            alpha = 0.1
            new_reliability = alpha * performance_score + (1 - alpha) * current_reliability
            self.agent_reliability[agent_id] = new_reliability
        
        # Update domain expertise
        task_domain = await self._identify_task_domain(task)
        for result in results:
            agent_id = result["agent_id"]
            if agent_id not in self.domain_expertise:
                self.domain_expertise[agent_id] = {}
            
            current_expertise = self.domain_expertise[agent_id].get(task_domain, 0.7)
            performance_score = result.get("confidence", 0.0) if result.get("success", False) else 0.0
            
            alpha = 0.1
            new_expertise = alpha * performance_score + (1 - alpha) * current_expertise
            self.domain_expertise[agent_id][task_domain] = new_expertise
        
        # Record consensus history
        consensus_record = {
            "timestamp": time.time(),
            "task": task,
            "method_used": consensus_result.method_used.value,
            "consensus_achieved": consensus_result.consensus_achieved,
            "agreement_level": consensus_result.agreement_level,
            "final_confidence": consensus_result.confidence_score,
            "participating_agents": consensus_result.participating_agents
        }
        
        self.consensus_history.append(consensus_record)
        
        # Limit history size
        if len(self.consensus_history) > 1000:
            self.consensus_history = self.consensus_history[-500:]
    
    async def _setup_consensus_methods(self) -> None:
        """Setup consensus methods"""
        self.consensus_methods = {
            method.value: method for method in ConsensusMethod
        }
    
    async def _setup_synthesis_strategies(self) -> None:
        """Setup synthesis strategies"""
        self.synthesis_strategies = {
            "simple": "Use single best response",
            "weighted": "Weight responses by confidence and reliability",
            "consensus": "Require agreement between multiple agents",
            "expert": "Defer to domain expert agent",
            "hybrid": "Combine multiple synthesis approaches"
        }
    
    async def _load_agent_reliability(self) -> None:
        """Load agent reliability data"""
        # Initialize with default reliability scores
        # In production, this would load from persistent storage
        self.agent_reliability = {}
        self.domain_expertise = {}
    
    async def _initialize_performance_tracking(self) -> None:
        """Initialize performance tracking for consensus methods"""
        for method in ConsensusMethod:
            self.method_performance[method] = {
                "usage_count": 0,
                "success_rate": 0.0,
                "average_confidence": 0.0,
                "average_agreement": 0.0
            }
    
    async def shutdown(self) -> None:
        """Shutdown collective intelligence system"""
        try:
            self.is_initialized = False
            logger.info("Collective Intelligence shutdown complete")
        except Exception as e:
            logger.error(f"Error during Collective Intelligence shutdown: {e}")
