"""
Voice Session Management for ThinkMesh AI
=========================================

Manages voice interaction sessions with state tracking,
conversation context, and performance optimization.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from ..interfaces import UserContext, VoiceInput, VoiceOutput
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class VoiceSessionConfig:
    """Voice session configuration"""
    max_session_duration: int = 3600  # 1 hour
    max_idle_time: int = 300  # 5 minutes
    auto_save_interval: int = 60  # 1 minute
    conversation_history_limit: int = 100
    enable_context_awareness: bool = True
    enable_interruption_handling: bool = True
    voice_activity_timeout: float = 2.0  # seconds


@dataclass
class ConversationTurn:
    """Single conversation turn"""
    turn_id: str
    timestamp: datetime
    user_input: str
    ai_response: str
    audio_input: Optional[VoiceInput] = None
    audio_output: Optional[VoiceOutput] = None
    processing_time: float = 0.0
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionMetrics:
    """Session performance metrics"""
    total_turns: int = 0
    total_processing_time: float = 0.0
    average_response_time: float = 0.0
    voice_activity_ratio: float = 0.0
    interruption_count: int = 0
    error_count: int = 0
    session_quality_score: float = 0.0


class VoiceSession:
    """
    Manages a voice interaction session with context tracking
    and performance optimization
    """
    
    def __init__(self, session_id: str, user_context: UserContext, 
                 config: VoiceSessionConfig):
        self.session_id = session_id
        self.user_context = user_context
        self.config = config
        
        # Session state
        self.is_active = False
        self.start_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self.conversation_history: List[ConversationTurn] = []
        
        # Session metrics
        self.metrics = SessionMetrics()
        
        # Event handlers
        self.on_turn_complete: Optional[Callable] = None
        self.on_session_timeout: Optional[Callable] = None
        self.on_interruption: Optional[Callable] = None
        
        # Internal state
        self._current_turn: Optional[ConversationTurn] = None
        self._auto_save_task: Optional[asyncio.Task] = None
        self._timeout_task: Optional[asyncio.Task] = None
        
    async def start_session(self) -> None:
        """Start the voice session"""
        try:
            if self.is_active:
                raise ThinkMeshException(
                    f"Session {self.session_id} is already active",
                    ErrorCode.VOICE_SESSION_ALREADY_ACTIVE
                )
            
            self.is_active = True
            self.start_time = datetime.now()
            self.last_activity = self.start_time
            
            # Start auto-save task
            if self.config.auto_save_interval > 0:
                self._auto_save_task = asyncio.create_task(self._auto_save_loop())
            
            # Start timeout monitoring
            self._timeout_task = asyncio.create_task(self._timeout_monitor())
            
            logger.info(f"Voice session {self.session_id} started")
            
        except Exception as e:
            logger.error(f"Failed to start voice session {self.session_id}: {e}")
            raise
    
    async def end_session(self) -> SessionMetrics:
        """End the voice session and return metrics"""
        try:
            if not self.is_active:
                logger.warning(f"Session {self.session_id} is not active")
                return self.metrics
            
            self.is_active = False
            
            # Cancel background tasks
            if self._auto_save_task:
                self._auto_save_task.cancel()
                try:
                    await self._auto_save_task
                except asyncio.CancelledError:
                    pass
            
            if self._timeout_task:
                self._timeout_task.cancel()
                try:
                    await self._timeout_task
                except asyncio.CancelledError:
                    pass
            
            # Complete current turn if active
            if self._current_turn:
                await self._complete_current_turn()
            
            # Calculate final metrics
            await self._calculate_session_metrics()
            
            # Save session data
            await self._save_session_data()
            
            logger.info(f"Voice session {self.session_id} ended. Metrics: {self.metrics}")
            return self.metrics
            
        except Exception as e:
            logger.error(f"Error ending voice session {self.session_id}: {e}")
            raise
    
    async def start_turn(self, voice_input: VoiceInput) -> str:
        """Start a new conversation turn"""
        try:
            if not self.is_active:
                raise ThinkMeshException(
                    f"Session {self.session_id} is not active",
                    ErrorCode.VOICE_SESSION_NOT_ACTIVE
                )
            
            # Complete previous turn if exists
            if self._current_turn:
                await self._complete_current_turn()
            
            # Create new turn
            turn_id = str(uuid.uuid4())
            self._current_turn = ConversationTurn(
                turn_id=turn_id,
                timestamp=datetime.now(),
                user_input="",  # Will be filled by STT
                ai_response="",  # Will be filled by AI processing
                audio_input=voice_input
            )
            
            # Update activity timestamp
            self.last_activity = datetime.now()
            
            logger.debug(f"Started turn {turn_id} in session {self.session_id}")
            return turn_id
            
        except Exception as e:
            logger.error(f"Error starting turn in session {self.session_id}: {e}")
            raise
    
    async def complete_turn(self, user_input: str, ai_response: str, 
                          voice_output: VoiceOutput, processing_time: float,
                          confidence_score: float = 0.0) -> None:
        """Complete the current conversation turn"""
        try:
            if not self._current_turn:
                raise ThinkMeshException(
                    "No active turn to complete",
                    ErrorCode.VOICE_NO_ACTIVE_TURN
                )
            
            # Update turn data
            self._current_turn.user_input = user_input
            self._current_turn.ai_response = ai_response
            self._current_turn.audio_output = voice_output
            self._current_turn.processing_time = processing_time
            self._current_turn.confidence_score = confidence_score
            
            # Add to conversation history
            self.conversation_history.append(self._current_turn)
            
            # Limit conversation history
            if len(self.conversation_history) > self.config.conversation_history_limit:
                self.conversation_history = self.conversation_history[-self.config.conversation_history_limit:]
            
            # Update metrics
            self.metrics.total_turns += 1
            self.metrics.total_processing_time += processing_time
            self.metrics.average_response_time = (
                self.metrics.total_processing_time / self.metrics.total_turns
            )
            
            # Call completion handler
            if self.on_turn_complete:
                try:
                    await self.on_turn_complete(self._current_turn)
                except Exception as e:
                    logger.error(f"Error in turn completion handler: {e}")
            
            logger.debug(f"Completed turn {self._current_turn.turn_id}")
            self._current_turn = None
            
        except Exception as e:
            logger.error(f"Error completing turn in session {self.session_id}: {e}")
            raise
    
    async def handle_interruption(self) -> None:
        """Handle user interruption during AI response"""
        try:
            if self._current_turn:
                self.metrics.interruption_count += 1
                
                # Mark turn as interrupted
                self._current_turn.metadata["interrupted"] = True
                
                # Call interruption handler
                if self.on_interruption:
                    try:
                        await self.on_interruption(self._current_turn)
                    except Exception as e:
                        logger.error(f"Error in interruption handler: {e}")
                
                logger.debug(f"Handled interruption in turn {self._current_turn.turn_id}")
            
        except Exception as e:
            logger.error(f"Error handling interruption in session {self.session_id}: {e}")
    
    async def get_conversation_context(self, max_turns: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context for AI processing"""
        try:
            recent_turns = self.conversation_history[-max_turns:] if max_turns > 0 else self.conversation_history
            
            context = []
            for turn in recent_turns:
                context.append({
                    "user": turn.user_input,
                    "assistant": turn.ai_response,
                    "timestamp": turn.timestamp.isoformat(),
                    "confidence": turn.confidence_score,
                    "metadata": turn.metadata
                })
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []
    
    async def update_user_context(self, updates: Dict[str, Any]) -> None:
        """Update user context during session"""
        try:
            # Update user context
            for key, value in updates.items():
                if hasattr(self.user_context, key):
                    setattr(self.user_context, key, value)
                else:
                    # Add to session data
                    self.user_context.session_data[key] = value
            
            logger.debug(f"Updated user context in session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error updating user context: {e}")
    
    async def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary and statistics"""
        try:
            duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            
            return {
                "session_id": self.session_id,
                "user_id": self.user_context.user_id,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "duration_seconds": duration,
                "is_active": self.is_active,
                "total_turns": len(self.conversation_history),
                "metrics": {
                    "total_turns": self.metrics.total_turns,
                    "average_response_time": self.metrics.average_response_time,
                    "interruption_count": self.metrics.interruption_count,
                    "error_count": self.metrics.error_count,
                    "session_quality_score": self.metrics.session_quality_score
                },
                "last_activity": self.last_activity.isoformat() if self.last_activity else None
            }
            
        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            return {}
    
    async def _complete_current_turn(self) -> None:
        """Complete current turn with default values"""
        if self._current_turn:
            # Add incomplete turn to history with metadata
            self._current_turn.metadata["incomplete"] = True
            self.conversation_history.append(self._current_turn)
            self._current_turn = None
    
    async def _auto_save_loop(self) -> None:
        """Auto-save session data periodically"""
        try:
            while self.is_active:
                await asyncio.sleep(self.config.auto_save_interval)
                if self.is_active:
                    await self._save_session_data()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in auto-save loop: {e}")
    
    async def _timeout_monitor(self) -> None:
        """Monitor session for timeouts"""
        try:
            while self.is_active:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                if not self.is_active:
                    break
                
                now = datetime.now()
                
                # Check session timeout
                if self.start_time and (now - self.start_time).total_seconds() > self.config.max_session_duration:
                    logger.info(f"Session {self.session_id} timed out (max duration)")
                    if self.on_session_timeout:
                        await self.on_session_timeout("max_duration")
                    break
                
                # Check idle timeout
                if self.last_activity and (now - self.last_activity).total_seconds() > self.config.max_idle_time:
                    logger.info(f"Session {self.session_id} timed out (idle)")
                    if self.on_session_timeout:
                        await self.on_session_timeout("idle")
                    break
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in timeout monitor: {e}")
    
    async def _calculate_session_metrics(self) -> None:
        """Calculate final session metrics"""
        try:
            if not self.conversation_history:
                return
            
            # Calculate quality score based on various factors
            factors = []
            
            # Response time factor (lower is better)
            if self.metrics.average_response_time > 0:
                response_time_score = max(0, 1 - (self.metrics.average_response_time - 1.0) / 5.0)
                factors.append(response_time_score)
            
            # Interruption factor (lower is better)
            if self.metrics.total_turns > 0:
                interruption_rate = self.metrics.interruption_count / self.metrics.total_turns
                interruption_score = max(0, 1 - interruption_rate * 2)
                factors.append(interruption_score)
            
            # Confidence factor
            avg_confidence = sum(turn.confidence_score for turn in self.conversation_history) / len(self.conversation_history)
            factors.append(avg_confidence)
            
            # Calculate overall quality score
            self.metrics.session_quality_score = sum(factors) / len(factors) if factors else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating session metrics: {e}")
    
    async def _save_session_data(self) -> None:
        """Save session data (placeholder for actual implementation)"""
        try:
            # In production, save to database or file system
            logger.debug(f"Saving session data for {self.session_id}")
            # TODO: Implement actual data persistence
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
