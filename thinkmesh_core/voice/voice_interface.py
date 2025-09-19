"""
Main Voice Interface for ThinkMesh AI
====================================

Premium voice interface integrating ElevenLabs TTS, Deepgram STT,
Silero VAD, and advanced audio processing for the highest quality
mobile voice experience.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
import logging
import time

from ..interfaces import IVoiceInterface, UserContext, VoiceInput, VoiceOutput
from ..config import VoiceConfig
from ..exceptions import ThinkMeshException, ErrorCode

from .audio_processor import AudioProcessor, AudioConfig
from .providers import ElevenLabsTTSProvider, DeepgramSTTProvider, SileroVADProvider
from .voice_session import VoiceSession, VoiceSessionConfig

logger = logging.getLogger(__name__)


class VoiceInterface(IVoiceInterface):
    """
    Premium voice interface providing studio-quality voice interactions
    with real-time processing and mobile optimization.
    """
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.is_initialized = False
        
        # Audio processing
        audio_config = AudioConfig(
            sample_rate=config.sample_rate,
            channels=config.channels,
            chunk_size=config.chunk_size,
            noise_suppression=config.noise_suppression,
            echo_cancellation=config.echo_cancellation,
            low_latency_mode=config.low_latency_mode
        )
        self.audio_processor = AudioProcessor(audio_config)
        
        # Voice service providers
        self.tts_provider: Optional[ElevenLabsTTSProvider] = None
        self.stt_provider: Optional[DeepgramSTTProvider] = None
        self.vad_provider: Optional[SileroVADProvider] = None
        
        # Session management
        self.active_sessions: Dict[str, VoiceSession] = {}
        self.session_config = VoiceSessionConfig()
        
        # Performance tracking
        self.total_requests = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        
    async def initialize(self) -> None:
        """Initialize the voice interface and all providers"""
        try:
            logger.info("Initializing ThinkMesh Voice Interface...")
            
            # Initialize audio processor
            await self.audio_processor.initialize()
            
            # Initialize TTS provider
            tts_config = {
                "api_key": self.config.__dict__.get("elevenlabs_api_key"),
                "voice_id": self.config.__dict__.get("elevenlabs_voice_id"),
                "model_id": self.config.__dict__.get("elevenlabs_model_id", "eleven_monolingual_v1"),
                "stability": 0.75,
                "similarity_boost": 0.75,
                "use_speaker_boost": True
            }
            self.tts_provider = ElevenLabsTTSProvider(tts_config)
            await self.tts_provider.initialize()
            
            # Initialize STT provider
            stt_config = {
                "api_key": self.config.__dict__.get("deepgram_api_key"),
                "model": "nova-2",
                "language": "en-US",
                "punctuate": True,
                "smart_format": True,
                "interim_results": False
            }
            self.stt_provider = DeepgramSTTProvider(stt_config)
            await self.stt_provider.initialize()
            
            # Initialize VAD provider
            vad_config = {
                "sample_rate": self.config.sample_rate,
                "threshold": 0.5,
                "min_speech_duration": 0.1,
                "min_silence_duration": 0.1
            }
            self.vad_provider = SileroVADProvider(vad_config)
            await self.vad_provider.initialize()
            
            self.is_initialized = True
            logger.info("Voice interface initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice interface: {e}")
            raise ThinkMeshException(
                f"Voice interface initialization failed: {e}",
                ErrorCode.VOICE_INITIALIZATION_FAILED
            )
    
    async def speech_to_text(self, voice_input: VoiceInput) -> str:
        """
        Convert speech to text using Deepgram STT with audio preprocessing
        """
        if not self.is_initialized:
            raise ThinkMeshException(
                "Voice interface not initialized",
                ErrorCode.VOICE_NOT_INITIALIZED
            )
        
        try:
            start_time = time.time()
            self.total_requests += 1
            
            # Process audio input
            processed_input = await self.audio_processor.process_input_audio(
                voice_input.audio_data, voice_input.format
            )
            
            # Perform voice activity detection
            vad_result = await self.vad_provider.detect_voice_activity(processed_input.audio_data)
            
            # Only process if speech is detected
            if not vad_result.get("has_speech", True):
                logger.debug("No speech detected in audio")
                return ""
            
            # Convert speech to text
            transcript = await self.stt_provider.speech_to_text(processed_input.audio_data)
            
            # Track performance
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            logger.debug(f"STT completed in {processing_time:.3f}s: '{transcript}'")
            return transcript
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Speech-to-text failed: {e}")
            raise ThinkMeshException(
                f"Speech-to-text conversion failed: {e}",
                ErrorCode.VOICE_STT_FAILED
            )
    
    async def text_to_speech(self, text: str, voice_config: Dict[str, Any]) -> VoiceOutput:
        """
        Convert text to speech using ElevenLabs TTS with audio enhancement
        """
        if not self.is_initialized:
            raise ThinkMeshException(
                "Voice interface not initialized",
                ErrorCode.VOICE_NOT_INITIALIZED
            )
        
        try:
            start_time = time.time()
            
            # Generate speech using TTS provider
            audio_data = await self.tts_provider.text_to_speech(text, voice_config)
            
            # Process output audio
            voice_output = await self.audio_processor.process_output_audio(
                audio_data, text, "wav"
            )
            
            # Track performance
            processing_time = time.time() - start_time
            
            logger.debug(f"TTS completed in {processing_time:.3f}s for {len(text)} characters")
            return voice_output
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Text-to-speech failed: {e}")
            raise ThinkMeshException(
                f"Text-to-speech conversion failed: {e}",
                ErrorCode.VOICE_TTS_FAILED
            )
    
    async def start_voice_session(self, user_context: UserContext) -> str:
        """
        Start a new voice interaction session
        """
        try:
            session_id = str(uuid.uuid4())
            
            # Create voice session
            voice_session = VoiceSession(session_id, user_context, self.session_config)
            
            # Set up event handlers
            voice_session.on_turn_complete = self._on_turn_complete
            voice_session.on_session_timeout = self._on_session_timeout
            voice_session.on_interruption = self._on_interruption
            
            # Start session
            await voice_session.start_session()
            
            # Store session
            self.active_sessions[session_id] = voice_session
            
            logger.info(f"Started voice session {session_id} for user {user_context.user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start voice session: {e}")
            raise ThinkMeshException(
                f"Voice session start failed: {e}",
                ErrorCode.VOICE_SESSION_START_FAILED
            )
    
    async def end_voice_session(self, session_id: str) -> None:
        """
        End a voice interaction session
        """
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found")
                return
            
            session = self.active_sessions[session_id]
            metrics = await session.end_session()
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info(f"Ended voice session {session_id}. Final metrics: {metrics}")
            
        except Exception as e:
            logger.error(f"Failed to end voice session {session_id}: {e}")
            raise ThinkMeshException(
                f"Voice session end failed: {e}",
                ErrorCode.VOICE_SESSION_END_FAILED
            )
    
    async def process_voice_interaction(self, session_id: str, voice_input: VoiceInput,
                                      ai_response_text: str) -> VoiceOutput:
        """
        Process a complete voice interaction (STT + TTS) within a session
        """
        try:
            if session_id not in self.active_sessions:
                raise ThinkMeshException(
                    f"Session {session_id} not found",
                    ErrorCode.VOICE_SESSION_NOT_FOUND
                )
            
            session = self.active_sessions[session_id]
            start_time = time.time()
            
            # Start new turn
            turn_id = await session.start_turn(voice_input)
            
            # Convert speech to text
            user_text = await self.speech_to_text(voice_input)
            
            # Convert AI response to speech
            voice_output = await self.text_to_speech(ai_response_text, {})
            
            # Complete turn
            processing_time = time.time() - start_time
            await session.complete_turn(
                user_input=user_text,
                ai_response=ai_response_text,
                voice_output=voice_output,
                processing_time=processing_time,
                confidence_score=0.95  # TODO: Calculate actual confidence
            )
            
            logger.debug(f"Processed voice interaction in {processing_time:.3f}s")
            return voice_output
            
        except Exception as e:
            logger.error(f"Voice interaction processing failed: {e}")
            raise
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a voice session"""
        try:
            if session_id not in self.active_sessions:
                return {}
            
            session = self.active_sessions[session_id]
            return await session.get_session_summary()
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return {}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get voice interface performance metrics"""
        try:
            # Audio processor metrics
            audio_metrics = await self.audio_processor.get_performance_metrics()
            
            # Interface metrics
            avg_processing_time = (
                self.total_processing_time / self.total_requests 
                if self.total_requests > 0 else 0.0
            )
            
            error_rate = (
                self.error_count / self.total_requests 
                if self.total_requests > 0 else 0.0
            )
            
            return {
                "total_requests": self.total_requests,
                "average_processing_time": avg_processing_time,
                "error_rate": error_rate,
                "active_sessions": len(self.active_sessions),
                "audio_processing": audio_metrics,
                "providers": {
                    "tts_initialized": self.tts_provider.is_initialized if self.tts_provider else False,
                    "stt_initialized": self.stt_provider.is_initialized if self.stt_provider else False,
                    "vad_initialized": self.vad_provider.is_initialized if self.vad_provider else False
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def shutdown(self) -> None:
        """Shutdown the voice interface"""
        try:
            logger.info("Shutting down voice interface...")
            
            # End all active sessions
            for session_id in list(self.active_sessions.keys()):
                await self.end_voice_session(session_id)
            
            # Shutdown providers
            if self.tts_provider:
                await self.tts_provider.shutdown()
            if self.stt_provider:
                await self.stt_provider.shutdown()
            if self.vad_provider:
                await self.vad_provider.shutdown()
            
            # Shutdown audio processor
            await self.audio_processor.shutdown()
            
            self.is_initialized = False
            logger.info("Voice interface shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during voice interface shutdown: {e}")
    
    # Event handlers
    async def _on_turn_complete(self, turn) -> None:
        """Handle turn completion"""
        logger.debug(f"Turn {turn.turn_id} completed")
    
    async def _on_session_timeout(self, reason: str) -> None:
        """Handle session timeout"""
        logger.info(f"Session timeout: {reason}")
    
    async def _on_interruption(self, turn) -> None:
        """Handle user interruption"""
        logger.debug(f"User interruption in turn {turn.turn_id}")
    
    # Health check implementation
    async def check_health(self) -> Dict[str, Any]:
        """Check health status of voice interface"""
        try:
            health_status = {
                "status": "healthy" if self.is_initialized else "unhealthy",
                "initialized": self.is_initialized,
                "active_sessions": len(self.active_sessions),
                "total_requests": self.total_requests,
                "error_count": self.error_count,
                "providers": {
                    "tts": self.tts_provider.is_initialized if self.tts_provider else False,
                    "stt": self.stt_provider.is_initialized if self.stt_provider else False,
                    "vad": self.vad_provider.is_initialized if self.vad_provider else False
                }
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get component performance metrics"""
        return await self.get_performance_metrics()
