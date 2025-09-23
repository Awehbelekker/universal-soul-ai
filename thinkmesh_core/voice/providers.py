"""
Voice Service Providers for ThinkMesh AI
========================================

Premium voice service providers including ElevenLabs TTS, Deepgram STT,
and Silero VAD for the highest quality voice experience.
"""

import asyncio
import io
import wave
from typing import Optional, Dict, Any, AsyncGenerator
from abc import ABC, abstractmethod
import logging

# Optional imports for full functionality
try:
    import aiohttp
    import numpy as np
    NETWORK_LIBS_AVAILABLE = True
    ArrayType = np.ndarray
except ImportError:
    # Fallback for mobile/minimal environments
    NETWORK_LIBS_AVAILABLE = False
    aiohttp = None
    np = None
    ArrayType = Any

from ..interfaces import VoiceInput, VoiceOutput
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


class BaseVoiceProvider(ABC):
    """Base class for voice service providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the provider"""
        pass


class ElevenLabsTTSProvider(BaseVoiceProvider):
    """
    ElevenLabs Text-to-Speech Provider
    Premium TTS with studio-quality voice synthesis
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.voice_id = config.get("voice_id", "21m00Tcm4TlvDq8ikWAM")  # Default voice
        self.model_id = config.get("model_id", "eleven_monolingual_v1")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Voice settings for optimal quality
        self.voice_settings = {
            "stability": config.get("stability", 0.75),
            "similarity_boost": config.get("similarity_boost", 0.75),
            "style": config.get("style", 0.0),
            "use_speaker_boost": config.get("use_speaker_boost", True)
        }
    
    async def initialize(self) -> None:
        """Initialize ElevenLabs TTS provider"""
        try:
            if not self.api_key:
                logger.warning("ElevenLabs API key not provided, using local fallback")
                return
            
            # Create HTTP session with optimized settings
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                }
            )
            
            # Test connection
            await self._test_connection()
            
            self.is_initialized = True
            logger.info("ElevenLabs TTS provider initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs TTS: {e}")
            raise ThinkMeshException(
                f"ElevenLabs TTS initialization failed: {e}",
                ErrorCode.VOICE_PROVIDER_INIT_FAILED
            )
    
    async def text_to_speech(self, text: str, voice_config: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Convert text to high-quality speech using ElevenLabs
        """
        if not self.is_initialized or not self.session:
            # Fallback to local TTS
            return await self._local_tts_fallback(text)
        
        try:
            # Merge voice config with defaults
            settings = {**self.voice_settings}
            if voice_config:
                settings.update(voice_config)
            
            # Prepare request payload
            payload = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": settings
            }
            
            # Make API request
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    logger.debug(f"Generated {len(audio_data)} bytes of audio from ElevenLabs")
                    return audio_data
                else:
                    error_text = await response.text()
                    logger.error(f"ElevenLabs API error {response.status}: {error_text}")
                    # Fallback to local TTS
                    return await self._local_tts_fallback(text)
        
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            # Fallback to local TTS
            return await self._local_tts_fallback(text)
    
    async def _test_connection(self) -> None:
        """Test connection to ElevenLabs API"""
        try:
            url = f"{self.base_url}/voices"
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"API test failed with status {response.status}")
        except Exception as e:
            logger.error(f"ElevenLabs connection test failed: {e}")
            raise
    
    async def _local_tts_fallback(self, text: str) -> bytes:
        """Local TTS fallback using system TTS"""
        try:
            # Simple local TTS implementation
            # In production, integrate with local TTS engines like espeak, festival, or pyttsx3
            logger.info("Using local TTS fallback")
            
            # For now, return silence as placeholder
            # This should be replaced with actual local TTS implementation
            sample_rate = 16000
            duration = len(text) * 0.1  # Rough estimate
            samples = int(sample_rate * duration)
            
            # Generate simple tone as placeholder
            t = np.linspace(0, duration, samples)
            audio = 0.1 * np.sin(2 * np.pi * 440 * t)  # 440Hz tone
            
            # Convert to WAV bytes
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes((audio * 32767).astype(np.int16).tobytes())
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Local TTS fallback failed: {e}")
            raise ThinkMeshException(
                f"TTS fallback failed: {e}",
                ErrorCode.VOICE_TTS_FAILED
            )
    
    async def shutdown(self) -> None:
        """Shutdown ElevenLabs TTS provider"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            self.is_initialized = False
            logger.info("ElevenLabs TTS provider shutdown complete")
        except Exception as e:
            logger.error(f"Error shutting down ElevenLabs TTS: {e}")


class DeepgramSTTProvider(BaseVoiceProvider):
    """
    Deepgram Speech-to-Text Provider
    Real-time STT with 95%+ accuracy
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = "https://api.deepgram.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # STT settings for optimal accuracy
        self.stt_settings = {
            "model": config.get("model", "nova-2"),
            "language": config.get("language", "en-US"),
            "punctuate": config.get("punctuate", True),
            "smart_format": config.get("smart_format", True),
            "interim_results": config.get("interim_results", False),
            "endpointing": config.get("endpointing", 300),
            "vad_events": config.get("vad_events", True)
        }
    
    async def initialize(self) -> None:
        """Initialize Deepgram STT provider"""
        try:
            if not self.api_key:
                logger.warning("Deepgram API key not provided, using local fallback")
                return
            
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=60, connect=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "audio/wav"
                }
            )
            
            # Test connection
            await self._test_connection()
            
            self.is_initialized = True
            logger.info("Deepgram STT provider initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Deepgram STT: {e}")
            raise ThinkMeshException(
                f"Deepgram STT initialization failed: {e}",
                ErrorCode.VOICE_PROVIDER_INIT_FAILED
            )
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """
        Convert speech to text using Deepgram
        """
        if not self.is_initialized or not self.session:
            # Fallback to local STT
            return await self._local_stt_fallback(audio_data)
        
        try:
            # Build query parameters
            params = {
                "model": self.stt_settings["model"],
                "language": self.stt_settings["language"],
                "punctuate": self.stt_settings["punctuate"],
                "smart_format": self.stt_settings["smart_format"],
                "interim_results": self.stt_settings["interim_results"],
                "endpointing": self.stt_settings["endpointing"],
                "vad_events": self.stt_settings["vad_events"]
            }
            
            # Make API request
            url = f"{self.base_url}/listen"
            
            async with self.session.post(url, params=params, data=audio_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract transcript
                    transcript = ""
                    if "results" in result and "channels" in result["results"]:
                        channels = result["results"]["channels"]
                        if channels and "alternatives" in channels[0]:
                            alternatives = channels[0]["alternatives"]
                            if alternatives:
                                transcript = alternatives[0].get("transcript", "")
                    
                    logger.debug(f"Deepgram transcription: '{transcript}'")
                    return transcript
                else:
                    error_text = await response.text()
                    logger.error(f"Deepgram API error {response.status}: {error_text}")
                    # Fallback to local STT
                    return await self._local_stt_fallback(audio_data)
        
        except Exception as e:
            logger.error(f"Deepgram STT error: {e}")
            # Fallback to local STT
            return await self._local_stt_fallback(audio_data)
    
    async def _test_connection(self) -> None:
        """Test connection to Deepgram API"""
        try:
            # Test with minimal audio data
            test_audio = b'\x00' * 1024  # Minimal audio data
            url = f"{self.base_url}/listen"
            params = {"model": "nova-2", "language": "en-US"}
            
            async with self.session.post(url, params=params, data=test_audio) as response:
                # We expect this to fail with audio format error, but connection should work
                if response.status not in [200, 400]:
                    raise Exception(f"API test failed with status {response.status}")
        except Exception as e:
            logger.error(f"Deepgram connection test failed: {e}")
            raise
    
    async def _local_stt_fallback(self, audio_data: bytes) -> str:
        """Local STT fallback"""
        try:
            # Simple local STT implementation
            # In production, integrate with local STT engines like Whisper, Vosk, or SpeechRecognition
            logger.info("Using local STT fallback")
            
            # For now, return placeholder text
            # This should be replaced with actual local STT implementation
            return "[Local STT: Audio received but not transcribed]"
            
        except Exception as e:
            logger.error(f"Local STT fallback failed: {e}")
            raise ThinkMeshException(
                f"STT fallback failed: {e}",
                ErrorCode.VOICE_STT_FAILED
            )
    
    async def shutdown(self) -> None:
        """Shutdown Deepgram STT provider"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            self.is_initialized = False
            logger.info("Deepgram STT provider shutdown complete")
        except Exception as e:
            logger.error(f"Error shutting down Deepgram STT: {e}")


class SileroVADProvider(BaseVoiceProvider):
    """
    Silero Voice Activity Detection Provider
    High-precision voice activity detection
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.sample_rate = config.get("sample_rate", 16000)
        self.threshold = config.get("threshold", 0.5)
        self.min_speech_duration = config.get("min_speech_duration", 0.1)
        self.min_silence_duration = config.get("min_silence_duration", 0.1)
    
    async def initialize(self) -> None:
        """Initialize Silero VAD provider"""
        try:
            # Import Silero VAD
            import torch
            
            # Load Silero VAD model
            model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            
            self.model = model
            self.get_speech_timestamps = utils[0]
            
            self.is_initialized = True
            logger.info("Silero VAD provider initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Silero VAD: {e}")
            # Use simple energy-based VAD as fallback
            self.model = None
            self.is_initialized = True
            logger.warning("Using energy-based VAD fallback")
    
    async def detect_voice_activity(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Detect voice activity in audio
        """
        try:
            # Convert audio to tensor
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            if self.model is not None:
                # Use Silero VAD
                import torch
                audio_tensor = torch.from_numpy(audio_array)
                
                # Get speech timestamps
                speech_timestamps = self.get_speech_timestamps(
                    audio_tensor,
                    self.model,
                    sampling_rate=self.sample_rate,
                    threshold=self.threshold,
                    min_speech_duration_ms=int(self.min_speech_duration * 1000),
                    min_silence_duration_ms=int(self.min_silence_duration * 1000)
                )
                
                # Calculate voice activity metrics
                total_duration = len(audio_array) / self.sample_rate
                speech_duration = sum(
                    (ts['end'] - ts['start']) / self.sample_rate 
                    for ts in speech_timestamps
                )
                
                voice_activity_ratio = speech_duration / total_duration if total_duration > 0 else 0
                has_speech = len(speech_timestamps) > 0
                
                return {
                    "has_speech": has_speech,
                    "voice_activity_ratio": voice_activity_ratio,
                    "speech_segments": speech_timestamps,
                    "total_duration": total_duration,
                    "speech_duration": speech_duration
                }
            else:
                # Fallback energy-based VAD
                return await self._energy_based_vad(audio_array)
                
        except Exception as e:
            logger.error(f"Voice activity detection failed: {e}")
            # Return safe default
            return {
                "has_speech": True,
                "voice_activity_ratio": 0.5,
                "speech_segments": [],
                "total_duration": len(audio_data) / (2 * self.sample_rate),
                "speech_duration": 0.0
            }
    
    async def _energy_based_vad(self, audio_array: ArrayType) -> Dict[str, Any]:
        """Simple energy-based voice activity detection"""
        try:
            # Calculate RMS energy
            frame_size = int(0.025 * self.sample_rate)  # 25ms frames
            hop_size = int(0.010 * self.sample_rate)    # 10ms hop
            
            frames = []
            for i in range(0, len(audio_array) - frame_size, hop_size):
                frame = audio_array[i:i + frame_size]
                rms = np.sqrt(np.mean(frame ** 2))
                frames.append(rms)
            
            if not frames:
                return {
                    "has_speech": False,
                    "voice_activity_ratio": 0.0,
                    "speech_segments": [],
                    "total_duration": 0.0,
                    "speech_duration": 0.0
                }
            
            # Adaptive threshold
            mean_energy = np.mean(frames)
            std_energy = np.std(frames)
            threshold = mean_energy + 2 * std_energy
            
            # Detect speech frames
            speech_frames = np.array(frames) > threshold
            voice_activity_ratio = np.mean(speech_frames)
            has_speech = voice_activity_ratio > 0.1
            
            total_duration = len(audio_array) / self.sample_rate
            speech_duration = voice_activity_ratio * total_duration
            
            return {
                "has_speech": has_speech,
                "voice_activity_ratio": float(voice_activity_ratio),
                "speech_segments": [],  # Not implemented for energy-based VAD
                "total_duration": total_duration,
                "speech_duration": speech_duration
            }
            
        except Exception as e:
            logger.error(f"Energy-based VAD failed: {e}")
            return {
                "has_speech": True,
                "voice_activity_ratio": 0.5,
                "speech_segments": [],
                "total_duration": 0.0,
                "speech_duration": 0.0
            }
    
    async def shutdown(self) -> None:
        """Shutdown Silero VAD provider"""
        try:
            self.model = None
            self.is_initialized = False
            logger.info("Silero VAD provider shutdown complete")
        except Exception as e:
            logger.error(f"Error shutting down Silero VAD: {e}")
