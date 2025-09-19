"""
Learning Engine for HRM Engine
==============================

Continuous learning component that implements the revolutionary 1000-sample learning
capability for user-specific adaptation and pattern recognition.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging

from ..config import HRMConfig
from ..interfaces import UserContext
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class LearningRecord:
    """Individual learning record structure"""
    timestamp: float
    user_id: str
    request: str
    strategy: Dict[str, Any]
    result: Dict[str, Any]
    feedback: Optional[Dict[str, Any]]
    effectiveness_score: float
    pattern_id: str


@dataclass
class UserPattern:
    """User-specific pattern structure"""
    pattern_id: str
    user_id: str
    pattern_type: str
    frequency: int
    success_rate: float
    last_seen: float
    characteristics: Dict[str, Any]
    adaptations: List[Dict[str, Any]]


class LearningEngine:
    """
    Continuous Learning Engine
    
    Implements the revolutionary 1000-sample learning capability that allows
    the HRM engine to adapt to individual users and improve performance
    through continuous interaction feedback.
    """
    
    def __init__(self, config: HRMConfig, mobile_optimizer=None):
        self.config = config
        self.mobile_optimizer = mobile_optimizer
        self.is_initialized = False
        
        # Learning state
        self.learning_records: List[LearningRecord] = []
        self.user_patterns: Dict[str, List[UserPattern]] = defaultdict(list)
        self.global_patterns: Dict[str, Any] = {}
        
        # Learning parameters
        self.max_learning_samples = 1000
        self.pattern_threshold = 3  # Minimum occurrences to form a pattern
        self.adaptation_rate = 0.1
        self.forgetting_factor = 0.95
        
        # Performance tracking
        self.learning_effectiveness: Dict[str, float] = {}
        self.adaptation_history: List[Dict[str, Any]] = []
    
    async def initialize(self) -> None:
        """Initialize the learning engine"""
        try:
            logger.info("Initializing Learning Engine...")
            
            # Load existing learning data
            await self._load_learning_data()
            
            # Initialize pattern recognition
            await self._initialize_pattern_recognition()
            
            # Setup learning optimization
            await self._setup_learning_optimization()
            
            self.is_initialized = True
            logger.info("Learning Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Learning Engine: {e}")
            raise ThinkMeshException(
                f"Learning Engine initialization failed: {e}",
                ErrorCode.HRM_INITIALIZATION_FAILED
            )
    
    async def learn_from_interaction(self, request: str, strategy: Dict[str, Any],
                                   result: Dict[str, Any], context: UserContext) -> bool:
        """Learn from a single interaction"""
        try:
            # Calculate effectiveness score
            effectiveness_score = await self._calculate_effectiveness(
                strategy, result, context
            )
            
            # Identify pattern
            pattern_id = await self._identify_pattern(request, strategy, context)
            
            # Create learning record
            learning_record = LearningRecord(
                timestamp=time.time(),
                user_id=context.user_id,
                request=request,
                strategy=strategy,
                result=result,
                feedback=None,  # Will be updated when feedback is received
                effectiveness_score=effectiveness_score,
                pattern_id=pattern_id
            )
            
            # Add to learning records
            await self._add_learning_record(learning_record)
            
            # Update user patterns
            await self._update_user_patterns(learning_record)
            
            # Apply adaptations if enough samples
            adaptations_applied = await self._apply_adaptations(context.user_id)
            
            logger.debug(f"Learning from interaction completed. Effectiveness: {effectiveness_score:.3f}")
            return adaptations_applied
            
        except Exception as e:
            logger.error(f"Learning from interaction failed: {e}")
            return False
    
    async def process_feedback(self, request: str, response: str,
                             feedback: Optional[Dict[str, Any]] = None) -> None:
        """Process user feedback for learning"""
        try:
            if not feedback:
                return
            
            # Find corresponding learning record
            learning_record = await self._find_learning_record(request, response)
            
            if learning_record:
                # Update learning record with feedback
                learning_record.feedback = feedback
                
                # Recalculate effectiveness with feedback
                updated_effectiveness = await self._calculate_effectiveness_with_feedback(
                    learning_record, feedback
                )
                learning_record.effectiveness_score = updated_effectiveness
                
                # Update patterns based on feedback
                await self._update_patterns_with_feedback(learning_record, feedback)
                
                logger.debug("Feedback processed and learning updated")
            
        except Exception as e:
            logger.error(f"Feedback processing failed: {e}")
    
    async def get_user_adaptations(self, user_id: str) -> Dict[str, Any]:
        """Get current adaptations for a specific user"""
        try:
            user_patterns = self.user_patterns.get(user_id, [])
            
            adaptations = {
                "preferred_approaches": await self._get_preferred_approaches(user_patterns),
                "response_style": await self._get_response_style(user_patterns),
                "complexity_preference": await self._get_complexity_preference(user_patterns),
                "domain_expertise": await self._get_domain_expertise(user_patterns),
                "interaction_patterns": await self._get_interaction_patterns(user_patterns)
            }
            
            return adaptations
            
        except Exception as e:
            logger.error(f"Failed to get user adaptations: {e}")
            return {}
    
    async def _calculate_effectiveness(self, strategy: Dict[str, Any],
                                     result: Dict[str, Any], context: UserContext) -> float:
        """Calculate effectiveness score for the interaction"""
        factors = []
        
        # Confidence score factor
        confidence = result.get("confidence_score", 0.5)
        factors.append(confidence)
        
        # Response time factor (faster is better, up to a point)
        response_time = result.get("performance_metrics", {}).get("execution_time_ms", 1000)
        time_factor = max(0.0, 1.0 - (response_time - 500) / 2000)  # Optimal around 500ms
        factors.append(time_factor)
        
        # Strategy complexity vs result quality
        complexity = strategy.get("complexity", 0.5)
        if complexity > 0.7 and confidence > 0.8:
            factors.append(0.9)  # Bonus for handling complex tasks well
        elif complexity < 0.3 and confidence > 0.9:
            factors.append(0.8)  # Good for simple tasks
        else:
            factors.append(0.6)  # Average
        
        # Domain match factor
        domain = strategy.get("domain", "general")
        if domain in ["technical", "analytical"] and confidence > 0.8:
            factors.append(0.85)
        else:
            factors.append(0.7)
        
        return sum(factors) / len(factors)
    
    async def _calculate_effectiveness_with_feedback(self, learning_record: LearningRecord,
                                                   feedback: Dict[str, Any]) -> float:
        """Recalculate effectiveness with user feedback"""
        base_effectiveness = learning_record.effectiveness_score
        
        # User satisfaction factor
        satisfaction = feedback.get("satisfaction", 0.5)
        
        # Usefulness factor
        usefulness = feedback.get("usefulness", 0.5)
        
        # Accuracy factor
        accuracy = feedback.get("accuracy", 0.5)
        
        # Combine with base effectiveness
        feedback_score = (satisfaction + usefulness + accuracy) / 3
        
        # Weighted combination (70% base, 30% feedback)
        return 0.7 * base_effectiveness + 0.3 * feedback_score
    
    async def _identify_pattern(self, request: str, strategy: Dict[str, Any],
                              context: UserContext) -> str:
        """Identify pattern for the interaction"""
        # Create pattern identifier based on key characteristics
        domain = strategy.get("domain", "general")
        intent = strategy.get("intent", "general_inquiry")
        complexity_level = "high" if strategy.get("complexity", 0) > 0.6 else "medium" if strategy.get("complexity", 0) > 0.3 else "low"
        
        pattern_id = f"{domain}_{intent}_{complexity_level}"
        return pattern_id
    
    async def _add_learning_record(self, learning_record: LearningRecord) -> None:
        """Add learning record and manage memory"""
        self.learning_records.append(learning_record)
        
        # Implement 1000-sample learning limit
        if len(self.learning_records) > self.max_learning_samples:
            # Remove oldest records, but keep diverse patterns
            await self._prune_learning_records()
    
    async def _prune_learning_records(self) -> None:
        """Prune learning records while maintaining diversity"""
        # Group by pattern
        pattern_groups = defaultdict(list)
        for record in self.learning_records:
            pattern_groups[record.pattern_id].append(record)
        
        # Keep most recent and most effective from each pattern
        pruned_records = []
        for pattern_id, records in pattern_groups.items():
            # Sort by effectiveness and recency
            sorted_records = sorted(records, 
                                  key=lambda r: (r.effectiveness_score, r.timestamp), 
                                  reverse=True)
            
            # Keep top records from each pattern
            keep_count = min(len(sorted_records), self.max_learning_samples // len(pattern_groups))
            pruned_records.extend(sorted_records[:keep_count])
        
        # If still too many, keep most recent overall
        if len(pruned_records) > self.max_learning_samples:
            pruned_records = sorted(pruned_records, key=lambda r: r.timestamp, reverse=True)
            pruned_records = pruned_records[:self.max_learning_samples]
        
        self.learning_records = pruned_records
        logger.debug(f"Pruned learning records to {len(self.learning_records)} samples")
    
    async def _update_user_patterns(self, learning_record: LearningRecord) -> None:
        """Update user-specific patterns"""
        user_id = learning_record.user_id
        pattern_id = learning_record.pattern_id
        
        # Find existing pattern or create new one
        existing_pattern = None
        for pattern in self.user_patterns[user_id]:
            if pattern.pattern_id == pattern_id:
                existing_pattern = pattern
                break
        
        if existing_pattern:
            # Update existing pattern
            existing_pattern.frequency += 1
            existing_pattern.last_seen = learning_record.timestamp
            
            # Update success rate (exponential moving average)
            alpha = self.adaptation_rate
            existing_pattern.success_rate = (
                alpha * learning_record.effectiveness_score + 
                (1 - alpha) * existing_pattern.success_rate
            )
            
            # Update characteristics
            await self._update_pattern_characteristics(existing_pattern, learning_record)
            
        else:
            # Create new pattern
            new_pattern = UserPattern(
                pattern_id=pattern_id,
                user_id=user_id,
                pattern_type=learning_record.strategy.get("domain", "general"),
                frequency=1,
                success_rate=learning_record.effectiveness_score,
                last_seen=learning_record.timestamp,
                characteristics=await self._extract_pattern_characteristics(learning_record),
                adaptations=[]
            )
            
            self.user_patterns[user_id].append(new_pattern)
    
    async def _extract_pattern_characteristics(self, learning_record: LearningRecord) -> Dict[str, Any]:
        """Extract characteristics from learning record"""
        return {
            "approach": learning_record.strategy.get("approach"),
            "complexity": learning_record.strategy.get("complexity"),
            "domain": learning_record.strategy.get("domain"),
            "intent": learning_record.strategy.get("intent"),
            "urgency": learning_record.strategy.get("urgency"),
            "response_time": learning_record.result.get("performance_metrics", {}).get("execution_time_ms"),
            "confidence": learning_record.result.get("confidence_score")
        }
    
    async def _update_pattern_characteristics(self, pattern: UserPattern, 
                                            learning_record: LearningRecord) -> None:
        """Update pattern characteristics with new data"""
        new_chars = await self._extract_pattern_characteristics(learning_record)
        
        # Update characteristics using exponential moving average
        alpha = self.adaptation_rate
        for key, new_value in new_chars.items():
            if key in pattern.characteristics and isinstance(new_value, (int, float)):
                pattern.characteristics[key] = (
                    alpha * new_value + (1 - alpha) * pattern.characteristics[key]
                )
            else:
                pattern.characteristics[key] = new_value
    
    async def _apply_adaptations(self, user_id: str) -> bool:
        """Apply adaptations based on learned patterns"""
        user_patterns = self.user_patterns.get(user_id, [])
        
        if not user_patterns:
            return False
        
        adaptations_applied = False
        
        # Apply adaptations for patterns with sufficient frequency
        for pattern in user_patterns:
            if pattern.frequency >= self.pattern_threshold:
                adaptation = await self._generate_adaptation(pattern)
                if adaptation:
                    pattern.adaptations.append(adaptation)
                    adaptations_applied = True
        
        return adaptations_applied
    
    async def _generate_adaptation(self, pattern: UserPattern) -> Optional[Dict[str, Any]]:
        """Generate adaptation based on pattern"""
        if pattern.success_rate > 0.8:
            # High success rate - reinforce this approach
            return {
                "type": "reinforce",
                "approach": pattern.characteristics.get("approach"),
                "confidence_boost": 0.1,
                "timestamp": time.time()
            }
        elif pattern.success_rate < 0.6:
            # Low success rate - try alternative approach
            return {
                "type": "alternative",
                "avoid_approach": pattern.characteristics.get("approach"),
                "suggested_complexity": pattern.characteristics.get("complexity", 0.5) * 0.8,
                "timestamp": time.time()
            }
        
        return None
    
    async def _get_preferred_approaches(self, user_patterns: List[UserPattern]) -> List[str]:
        """Get user's preferred approaches"""
        approach_scores = defaultdict(float)
        
        for pattern in user_patterns:
            approach = pattern.characteristics.get("approach")
            if approach:
                approach_scores[approach] += pattern.success_rate * pattern.frequency
        
        # Sort by score and return top approaches
        sorted_approaches = sorted(approach_scores.items(), key=lambda x: x[1], reverse=True)
        return [approach for approach, score in sorted_approaches[:3]]
    
    async def _get_response_style(self, user_patterns: List[UserPattern]) -> Dict[str, Any]:
        """Get user's preferred response style"""
        total_weight = sum(p.frequency for p in user_patterns)
        if total_weight == 0:
            return {"style": "balanced"}
        
        avg_complexity = sum(p.characteristics.get("complexity", 0.5) * p.frequency 
                           for p in user_patterns) / total_weight
        
        avg_response_time = sum(p.characteristics.get("response_time", 1000) * p.frequency 
                              for p in user_patterns) / total_weight
        
        return {
            "preferred_complexity": avg_complexity,
            "preferred_response_time": avg_response_time,
            "style": "detailed" if avg_complexity > 0.6 else "concise" if avg_complexity < 0.4 else "balanced"
        }
    
    async def _get_complexity_preference(self, user_patterns: List[UserPattern]) -> float:
        """Get user's complexity preference"""
        if not user_patterns:
            return 0.5
        
        total_weight = sum(p.frequency for p in user_patterns)
        weighted_complexity = sum(p.characteristics.get("complexity", 0.5) * p.frequency 
                                for p in user_patterns)
        
        return weighted_complexity / total_weight if total_weight > 0 else 0.5
    
    async def _get_domain_expertise(self, user_patterns: List[UserPattern]) -> Dict[str, float]:
        """Get user's domain expertise levels"""
        domain_scores = defaultdict(list)
        
        for pattern in user_patterns:
            domain = pattern.characteristics.get("domain", "general")
            domain_scores[domain].append(pattern.success_rate)
        
        # Calculate average success rate per domain
        domain_expertise = {}
        for domain, scores in domain_scores.items():
            domain_expertise[domain] = sum(scores) / len(scores)
        
        return domain_expertise
    
    async def _get_interaction_patterns(self, user_patterns: List[UserPattern]) -> Dict[str, Any]:
        """Get user's interaction patterns"""
        if not user_patterns:
            return {}
        
        total_interactions = sum(p.frequency for p in user_patterns)
        most_common_pattern = max(user_patterns, key=lambda p: p.frequency)
        
        return {
            "total_interactions": total_interactions,
            "most_common_pattern": most_common_pattern.pattern_id,
            "pattern_diversity": len(user_patterns),
            "average_success_rate": sum(p.success_rate for p in user_patterns) / len(user_patterns)
        }
    
    async def _find_learning_record(self, request: str, response: str) -> Optional[LearningRecord]:
        """Find learning record for feedback processing"""
        # Simple matching - in production, use more sophisticated matching
        for record in reversed(self.learning_records):  # Start from most recent
            if record.request == request:
                return record
        return None
    
    async def _update_patterns_with_feedback(self, learning_record: LearningRecord,
                                           feedback: Dict[str, Any]) -> None:
        """Update patterns based on user feedback"""
        # Update the pattern's success rate based on feedback
        user_patterns = self.user_patterns.get(learning_record.user_id, [])
        
        for pattern in user_patterns:
            if pattern.pattern_id == learning_record.pattern_id:
                # Incorporate feedback into success rate
                feedback_score = (
                    feedback.get("satisfaction", 0.5) + 
                    feedback.get("usefulness", 0.5) + 
                    feedback.get("accuracy", 0.5)
                ) / 3
                
                # Update with exponential moving average
                alpha = self.adaptation_rate
                pattern.success_rate = alpha * feedback_score + (1 - alpha) * pattern.success_rate
                break
    
    async def _load_learning_data(self) -> None:
        """Load existing learning data"""
        # In production, this would load from persistent storage
        logger.debug("Learning data loaded (simulated)")
    
    async def _initialize_pattern_recognition(self) -> None:
        """Initialize pattern recognition system"""
        # Initialize pattern recognition algorithms
        logger.debug("Pattern recognition initialized")
    
    async def _setup_learning_optimization(self) -> None:
        """Setup learning optimization"""
        # Configure learning parameters for mobile optimization
        if self.mobile_optimizer:
            optimized_params = await self.mobile_optimizer.optimize_learning_parameters({
                "max_samples": self.max_learning_samples,
                "adaptation_rate": self.adaptation_rate,
                "pattern_threshold": self.pattern_threshold
            })
            
            self.max_learning_samples = optimized_params.get("max_samples", self.max_learning_samples)
            self.adaptation_rate = optimized_params.get("adaptation_rate", self.adaptation_rate)
            self.pattern_threshold = optimized_params.get("pattern_threshold", self.pattern_threshold)
    
    async def shutdown(self) -> None:
        """Shutdown the learning engine"""
        try:
            # Save learning data before shutdown
            await self._save_learning_data()
            
            self.is_initialized = False
            logger.info("Learning Engine shutdown complete")
        except Exception as e:
            logger.error(f"Error during Learning Engine shutdown: {e}")
    
    async def _save_learning_data(self) -> None:
        """Save learning data to persistent storage"""
        # In production, this would save to persistent storage
        logger.debug("Learning data saved (simulated)")
