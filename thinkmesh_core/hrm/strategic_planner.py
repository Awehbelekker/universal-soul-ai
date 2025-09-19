"""
Strategic Planner for HRM Engine
===============================

High-level strategic planning component that operates on hours-to-days timescale
for abstract reasoning and goal decomposition.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from ..config import HRMConfig
from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class StrategicPlan:
    """Strategic plan structure"""
    goal: str
    approach: str
    key_steps: List[str]
    priority_level: int
    estimated_complexity: float
    context_requirements: List[str]
    success_criteria: List[str]
    resource_requirements: Dict[str, Any]
    timeline_estimate: str


class StrategicPlanner:
    """
    Strategic Planning Component
    
    Handles high-level, abstract reasoning for complex goals and long-term planning.
    Operates on hours-to-days timescale for strategic decision making.
    """
    
    def __init__(self, config: HRMConfig, mobile_optimizer=None):
        self.config = config
        self.mobile_optimizer = mobile_optimizer
        self.is_initialized = False
        
        # Strategic knowledge base
        self.strategic_patterns: Dict[str, Any] = {}
        self.goal_templates: Dict[str, List[str]] = {}
        self.success_metrics: Dict[str, Any] = {}
        
        # Learning state
        self.strategic_memory: List[Dict[str, Any]] = []
        self.pattern_effectiveness: Dict[str, float] = {}
    
    async def initialize(self) -> None:
        """Initialize the strategic planner"""
        try:
            logger.info("Initializing Strategic Planner...")
            
            # Load strategic patterns and templates
            await self._load_strategic_patterns()
            await self._load_goal_templates()
            await self._load_success_metrics()
            
            self.is_initialized = True
            logger.info("Strategic Planner initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Strategic Planner: {e}")
            raise ThinkMeshException(
                f"Strategic Planner initialization failed: {e}",
                ErrorCode.HRM_INITIALIZATION_FAILED
            )
    
    async def create_strategy(self, request: str, context: UserContext, 
                            constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create strategic plan for the given request"""
        try:
            # Analyze request complexity and scope
            analysis = await self._analyze_request(request, context)
            
            # Determine strategic approach
            approach = await self._determine_approach(analysis, constraints)
            
            # Generate strategic plan
            strategic_plan = await self._generate_strategic_plan(
                request, analysis, approach, context
            )
            
            # Optimize for mobile constraints
            if self.mobile_optimizer and constraints:
                strategic_plan = await self.mobile_optimizer.optimize_strategy(
                    strategic_plan, constraints
                )
            
            # Store in strategic memory
            await self._store_strategic_decision(request, strategic_plan, context)
            
            logger.debug(f"Strategic plan created: {strategic_plan['approach']}")
            return strategic_plan
            
        except Exception as e:
            logger.error(f"Strategic planning failed: {e}")
            raise ThinkMeshException(
                f"Strategic planning failed: {e}",
                ErrorCode.HRM_PROCESSING_FAILED
            )
    
    async def _analyze_request(self, request: str, context: UserContext) -> Dict[str, Any]:
        """Analyze request for strategic planning"""
        analysis = {
            "complexity": await self._assess_complexity(request),
            "scope": await self._assess_scope(request),
            "urgency": await self._assess_urgency(request, context),
            "domain": await self._identify_domain(request),
            "user_intent": await self._analyze_intent(request),
            "context_dependencies": await self._identify_context_dependencies(request, context)
        }
        
        return analysis
    
    async def _assess_complexity(self, request: str) -> float:
        """Assess complexity of the request (0.0 to 1.0)"""
        complexity_factors = []
        
        # Length factor
        length_factor = min(len(request.split()) / 100, 1.0)
        complexity_factors.append(length_factor)
        
        # Question complexity
        question_words = ["how", "why", "what", "when", "where", "which", "who"]
        question_count = sum(1 for word in question_words if word in request.lower())
        question_factor = min(question_count / 3, 1.0)
        complexity_factors.append(question_factor)
        
        # Technical complexity
        technical_terms = ["implement", "design", "architecture", "algorithm", "system", "optimize"]
        tech_count = sum(1 for term in technical_terms if term in request.lower())
        tech_factor = min(tech_count / 3, 1.0)
        complexity_factors.append(tech_factor)
        
        # Multi-step indicators
        step_indicators = ["first", "then", "next", "finally", "also", "additionally"]
        step_count = sum(1 for indicator in step_indicators if indicator in request.lower())
        step_factor = min(step_count / 3, 1.0)
        complexity_factors.append(step_factor)
        
        return sum(complexity_factors) / len(complexity_factors)
    
    async def _assess_scope(self, request: str) -> str:
        """Assess scope of the request"""
        scope_indicators = {
            "narrow": ["specific", "particular", "exact", "precise"],
            "medium": ["general", "typical", "common", "standard"],
            "broad": ["comprehensive", "complete", "full", "entire", "all"]
        }
        
        for scope, indicators in scope_indicators.items():
            if any(indicator in request.lower() for indicator in indicators):
                return scope
        
        # Default based on length
        word_count = len(request.split())
        if word_count < 10:
            return "narrow"
        elif word_count < 30:
            return "medium"
        else:
            return "broad"
    
    async def _assess_urgency(self, request: str, context: UserContext) -> str:
        """Assess urgency of the request"""
        urgent_indicators = ["urgent", "asap", "immediately", "critical", "emergency", "now"]
        if any(indicator in request.lower() for indicator in urgent_indicators):
            return "high"
        
        important_indicators = ["important", "priority", "need", "required", "must"]
        if any(indicator in request.lower() for indicator in important_indicators):
            return "medium"
        
        return "low"
    
    async def _identify_domain(self, request: str) -> str:
        """Identify the domain/category of the request"""
        domain_keywords = {
            "technical": ["code", "programming", "software", "system", "algorithm", "technical"],
            "creative": ["create", "design", "write", "generate", "creative", "artistic"],
            "analytical": ["analyze", "compare", "evaluate", "assess", "research", "study"],
            "informational": ["what", "who", "when", "where", "explain", "describe"],
            "problem_solving": ["solve", "fix", "troubleshoot", "debug", "resolve", "help"],
            "conversational": ["chat", "talk", "discuss", "conversation", "opinion"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in request.lower() for keyword in keywords):
                return domain
        
        return "general"
    
    async def _analyze_intent(self, request: str) -> str:
        """Analyze user intent"""
        intent_patterns = {
            "information_seeking": ["what", "who", "when", "where", "explain", "tell me"],
            "task_completion": ["do", "make", "create", "build", "implement", "execute"],
            "problem_solving": ["how", "solve", "fix", "help", "troubleshoot"],
            "decision_support": ["should", "recommend", "suggest", "advise", "choose"],
            "learning": ["learn", "understand", "teach", "show", "tutorial"],
            "creative": ["write", "design", "generate", "create", "compose"]
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in request.lower() for pattern in patterns):
                return intent
        
        return "general_inquiry"
    
    async def _identify_context_dependencies(self, request: str, context: UserContext) -> List[str]:
        """Identify what context is needed"""
        dependencies = []
        
        # Personal context indicators
        personal_indicators = ["my", "i", "me", "mine", "personal"]
        if any(indicator in request.lower() for indicator in personal_indicators):
            dependencies.append("user_personal_context")
        
        # Historical context indicators
        history_indicators = ["previous", "earlier", "before", "last time", "history"]
        if any(indicator in request.lower() for indicator in history_indicators):
            dependencies.append("conversation_history")
        
        # Current context indicators
        current_indicators = ["current", "now", "today", "this", "present"]
        if any(indicator in request.lower() for indicator in current_indicators):
            dependencies.append("current_context")
        
        # Domain-specific context
        if "project" in request.lower():
            dependencies.append("project_context")
        if "work" in request.lower():
            dependencies.append("work_context")
        
        return dependencies
    
    async def _determine_approach(self, analysis: Dict[str, Any], 
                                constraints: Optional[Dict[str, Any]]) -> str:
        """Determine strategic approach based on analysis"""
        complexity = analysis["complexity"]
        domain = analysis["domain"]
        intent = analysis["intent"]
        urgency = analysis["urgency"]
        
        # High complexity requires decomposition
        if complexity > 0.7:
            return "hierarchical_decomposition"
        
        # Technical domain with medium complexity
        if domain == "technical" and complexity > 0.4:
            return "systematic_analysis"
        
        # Creative tasks
        if domain == "creative" or intent == "creative":
            return "generative_exploration"
        
        # Problem solving
        if intent == "problem_solving":
            return "analytical_problem_solving"
        
        # Information seeking
        if intent == "information_seeking":
            return "knowledge_retrieval"
        
        # High urgency with low complexity
        if urgency == "high" and complexity < 0.5:
            return "direct_response"
        
        # Default approach
        return "contextual_reasoning"
    
    async def _generate_strategic_plan(self, request: str, analysis: Dict[str, Any],
                                     approach: str, context: UserContext) -> Dict[str, Any]:
        """Generate the strategic plan"""
        plan = {
            "goal": request,
            "approach": approach,
            "complexity": analysis["complexity"],
            "domain": analysis["domain"],
            "intent": analysis["intent"],
            "urgency": analysis["urgency"],
            "key_steps": await self._generate_key_steps(approach, analysis),
            "success_criteria": await self._define_success_criteria(approach, analysis),
            "resource_requirements": await self._estimate_resources(analysis),
            "timeline_estimate": await self._estimate_timeline(analysis),
            "context_requirements": analysis["context_dependencies"],
            "user_message": await self._generate_user_message(approach, analysis)
        }
        
        return plan
    
    async def _generate_key_steps(self, approach: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate key strategic steps"""
        step_templates = {
            "hierarchical_decomposition": [
                "Break down complex goal into sub-goals",
                "Prioritize sub-goals by importance and dependencies",
                "Plan execution sequence",
                "Synthesize results"
            ],
            "systematic_analysis": [
                "Gather relevant information",
                "Analyze systematically",
                "Identify patterns and insights",
                "Present structured findings"
            ],
            "generative_exploration": [
                "Explore creative possibilities",
                "Generate multiple alternatives",
                "Refine and enhance ideas",
                "Present creative solution"
            ],
            "analytical_problem_solving": [
                "Define problem clearly",
                "Analyze root causes",
                "Generate solution options",
                "Recommend optimal solution"
            ],
            "knowledge_retrieval": [
                "Identify information requirements",
                "Search relevant knowledge",
                "Synthesize information",
                "Present comprehensive answer"
            ],
            "direct_response": [
                "Understand immediate need",
                "Provide direct solution"
            ],
            "contextual_reasoning": [
                "Consider context and background",
                "Apply reasoning to situation",
                "Generate contextual response"
            ]
        }
        
        return step_templates.get(approach, ["Analyze request", "Generate response"])
    
    async def _define_success_criteria(self, approach: str, analysis: Dict[str, Any]) -> List[str]:
        """Define success criteria for the strategic plan"""
        base_criteria = ["Addresses user request accurately", "Response is clear and helpful"]
        
        approach_criteria = {
            "hierarchical_decomposition": ["All sub-goals addressed", "Logical structure maintained"],
            "systematic_analysis": ["Analysis is thorough", "Insights are valuable"],
            "generative_exploration": ["Solution is creative", "Meets requirements"],
            "analytical_problem_solving": ["Problem is solved", "Solution is practical"],
            "knowledge_retrieval": ["Information is accurate", "Coverage is comprehensive"],
            "direct_response": ["Response is immediate", "Need is satisfied"],
            "contextual_reasoning": ["Context is considered", "Response is appropriate"]
        }
        
        return base_criteria + approach_criteria.get(approach, [])
    
    async def _estimate_resources(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resource requirements"""
        complexity = analysis["complexity"]
        
        return {
            "processing_intensity": "high" if complexity > 0.7 else "medium" if complexity > 0.4 else "low",
            "memory_usage": "high" if complexity > 0.6 else "medium" if complexity > 0.3 else "low",
            "response_time_target": "fast" if analysis["urgency"] == "high" else "normal"
        }
    
    async def _estimate_timeline(self, analysis: Dict[str, Any]) -> str:
        """Estimate timeline for completion"""
        complexity = analysis["complexity"]
        urgency = analysis["urgency"]
        
        if urgency == "high":
            return "immediate"
        elif complexity > 0.7:
            return "extended"
        elif complexity > 0.4:
            return "moderate"
        else:
            return "quick"
    
    async def _generate_user_message(self, approach: str, analysis: Dict[str, Any]) -> str:
        """Generate user-facing message about the strategic approach"""
        messages = {
            "hierarchical_decomposition": "I'll break this down into manageable parts and work through them systematically.",
            "systematic_analysis": "Let me analyze this systematically to provide you with comprehensive insights.",
            "generative_exploration": "I'll explore creative approaches to develop an innovative solution for you.",
            "analytical_problem_solving": "I'll analyze the problem and work through potential solutions step by step.",
            "knowledge_retrieval": "Let me gather and synthesize the relevant information for you.",
            "direct_response": "I'll provide you with a direct answer to your immediate need.",
            "contextual_reasoning": "I'll consider the context and provide a thoughtful response."
        }
        
        return messages.get(approach, "I'll work on this request for you.")
    
    async def _store_strategic_decision(self, request: str, plan: Dict[str, Any], 
                                      context: UserContext) -> None:
        """Store strategic decision for learning"""
        decision_record = {
            "timestamp": time.time(),
            "request": request,
            "approach": plan["approach"],
            "complexity": plan["complexity"],
            "domain": plan["domain"],
            "user_id": context.user_id,
            "plan": plan
        }
        
        self.strategic_memory.append(decision_record)
        
        # Limit memory size
        if len(self.strategic_memory) > 1000:
            self.strategic_memory = self.strategic_memory[-500:]
    
    async def _load_strategic_patterns(self) -> None:
        """Load strategic patterns from knowledge base"""
        # Initialize with basic patterns
        self.strategic_patterns = {
            "complexity_thresholds": {
                "simple": 0.3,
                "moderate": 0.6,
                "complex": 0.8
            },
            "approach_effectiveness": {
                "hierarchical_decomposition": 0.85,
                "systematic_analysis": 0.80,
                "generative_exploration": 0.75,
                "analytical_problem_solving": 0.82,
                "knowledge_retrieval": 0.88,
                "direct_response": 0.90,
                "contextual_reasoning": 0.78
            }
        }
    
    async def _load_goal_templates(self) -> None:
        """Load goal decomposition templates"""
        self.goal_templates = {
            "technical_implementation": [
                "Requirements analysis",
                "Design planning",
                "Implementation",
                "Testing and validation"
            ],
            "problem_analysis": [
                "Problem definition",
                "Root cause analysis",
                "Solution generation",
                "Solution evaluation"
            ],
            "creative_project": [
                "Concept exploration",
                "Idea development",
                "Creative execution",
                "Refinement and polish"
            ]
        }
    
    async def _load_success_metrics(self) -> None:
        """Load success metrics definitions"""
        self.success_metrics = {
            "accuracy": "Response addresses the request correctly",
            "completeness": "All aspects of the request are covered",
            "clarity": "Response is clear and understandable",
            "usefulness": "Response provides practical value",
            "efficiency": "Response is generated in reasonable time"
        }
    
    async def shutdown(self) -> None:
        """Shutdown the strategic planner"""
        try:
            self.is_initialized = False
            logger.info("Strategic Planner shutdown complete")
        except Exception as e:
            logger.error(f"Error during Strategic Planner shutdown: {e}")
