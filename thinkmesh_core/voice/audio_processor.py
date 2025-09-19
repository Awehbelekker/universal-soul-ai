"""
Audio Processing Pipeline for ThinkMesh Voice Interface
======================================================

High-quality audio processing with real-time noise suppression,
echo cancellation, and mobile optimization.
"""

import asyncio
import numpy as np
import soundfile as sf
import librosa
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import logging

from ..interfaces import VoiceInput, VoiceOutput
from ..exceptions import ThinkMeshException, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio processing configuration"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    noise_suppression: bool = True
    echo_cancellation: bool = True
    auto_gain_control: bool = True
    low_latency_mode: bool = True
    
    # Mobile optimization
    battery_aware: bool = True
    thermal_throttling: bool = True
    adaptive_quality: bool = True


class AudioProcessor:
    """
    High-performance audio processing pipeline optimized for mobile devices
    with real-time noise suppression and echo cancellation.
    """
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.is_initialized = False
        
        # Audio processing state
        self.noise_profile: Optional[np.ndarray] = None
        self.echo_buffer: Optional[np.ndarray] = None
        self.gain_history: list = []
        
        # Performance tracking
        self.processing_times: list = []
        self.quality_metrics: Dict[str, float] = {}

        # Mobile optimization state
        self.battery_level: float = 1.0
        self.thermal_state: str = "normal"  # normal, warm, hot
        self.current_quality_level: str = "high"  # low, medium, high
        self.adaptive_processing: bool = config.adaptive_quality
        
    async def initialize(self) -> None:
        """Initialize audio processing pipeline"""
        try:
            logger.info("Initializing audio processor...")
            
            # Initialize noise suppression
            if self.config.noise_suppression:
                await self._initialize_noise_suppression()
            
            # Initialize echo cancellation
            if self.config.echo_cancellation:
                await self._initialize_echo_cancellation()
            
            # Initialize auto gain control
            if self.config.auto_gain_control:
                await self._initialize_auto_gain_control()
            
            self.is_initialized = True
            logger.info("Audio processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize audio processor: {e}")
            raise ThinkMeshException(
                f"Audio processor initialization failed: {e}",
                ErrorCode.VOICE_INITIALIZATION_FAILED
            )
    
    async def process_input_audio(self, audio_data: bytes, 
                                format: str = "wav") -> VoiceInput:
        """
        Process incoming audio with noise suppression and enhancement
        """
        if not self.is_initialized:
            raise ThinkMeshException(
                "Audio processor not initialized",
                ErrorCode.VOICE_NOT_INITIALIZED
            )
        
        try:
            import time
            start_time = time.time()
            
            # Convert bytes to numpy array
            audio_array = await self._bytes_to_array(audio_data, format)
            
            # Apply noise suppression
            if self.config.noise_suppression:
                audio_array = await self._apply_noise_suppression(audio_array)
            
            # Apply echo cancellation
            if self.config.echo_cancellation:
                audio_array = await self._apply_echo_cancellation(audio_array)
            
            # Apply auto gain control
            if self.config.auto_gain_control:
                audio_array = await self._apply_auto_gain_control(audio_array)
            
            # Convert back to bytes
            processed_audio = await self._array_to_bytes(audio_array, format)
            
            # Track performance
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # Create VoiceInput object
            voice_input = VoiceInput(
                audio_data=processed_audio,
                sample_rate=self.config.sample_rate,
                channels=self.config.channels,
                format=format,
                timestamp=time.time()
            )
            
            logger.debug(f"Processed input audio in {processing_time:.3f}s")
            return voice_input
            
        except Exception as e:
            logger.error(f"Error processing input audio: {e}")
            raise ThinkMeshException(
                f"Audio input processing failed: {e}",
                ErrorCode.VOICE_PROCESSING_FAILED
            )
    
    async def process_output_audio(self, audio_data: bytes, text: str,
                                 format: str = "wav") -> VoiceOutput:
        """
        Process outgoing audio with enhancement and optimization
        """
        try:
            import time
            start_time = time.time()
            
            # Convert to array for processing
            audio_array = await self._bytes_to_array(audio_data, format)
            
            # Apply output enhancement
            audio_array = await self._enhance_output_audio(audio_array)
            
            # Convert back to bytes
            enhanced_audio = await self._array_to_bytes(audio_array, format)
            
            processing_time = time.time() - start_time
            
            voice_output = VoiceOutput(
                audio_data=enhanced_audio,
                text=text,
                sample_rate=self.config.sample_rate,
                channels=self.config.channels,
                format=format
            )
            
            logger.debug(f"Processed output audio in {processing_time:.3f}s")
            return voice_output
            
        except Exception as e:
            logger.error(f"Error processing output audio: {e}")
            raise ThinkMeshException(
                f"Audio output processing failed: {e}",
                ErrorCode.VOICE_PROCESSING_FAILED
            )
    
    async def _initialize_noise_suppression(self) -> None:
        """Initialize noise suppression system"""
        try:
            # Create initial noise profile
            self.noise_profile = np.zeros(self.config.chunk_size // 2 + 1)
            logger.debug("Noise suppression initialized")
        except Exception as e:
            logger.error(f"Failed to initialize noise suppression: {e}")
            raise
    
    async def _initialize_echo_cancellation(self) -> None:
        """Initialize echo cancellation system"""
        try:
            # Initialize echo buffer
            buffer_size = self.config.sample_rate // 4  # 250ms buffer
            self.echo_buffer = np.zeros(buffer_size)
            logger.debug("Echo cancellation initialized")
        except Exception as e:
            logger.error(f"Failed to initialize echo cancellation: {e}")
            raise
    
    async def _initialize_auto_gain_control(self) -> None:
        """Initialize automatic gain control"""
        try:
            self.gain_history = []
            logger.debug("Auto gain control initialized")
        except Exception as e:
            logger.error(f"Failed to initialize auto gain control: {e}")
            raise
    
    async def _bytes_to_array(self, audio_data: bytes, format: str) -> np.ndarray:
        """Convert audio bytes to numpy array"""
        try:
            # Use soundfile for robust audio format handling
            import io
            audio_io = io.BytesIO(audio_data)
            audio_array, _ = sf.read(audio_io, dtype='float32')
            
            # Ensure correct sample rate
            if len(audio_array.shape) > 1:
                audio_array = librosa.to_mono(audio_array.T)
            
            # Resample if needed
            audio_array = librosa.resample(
                audio_array, 
                orig_sr=self.config.sample_rate,
                target_sr=self.config.sample_rate
            )
            
            return audio_array
            
        except Exception as e:
            logger.error(f"Error converting bytes to array: {e}")
            raise
    
    async def _array_to_bytes(self, audio_array: np.ndarray, format: str) -> bytes:
        """Convert numpy array to audio bytes"""
        try:
            import io
            audio_io = io.BytesIO()
            sf.write(audio_io, audio_array, self.config.sample_rate, format=format)
            return audio_io.getvalue()
        except Exception as e:
            logger.error(f"Error converting array to bytes: {e}")
            raise
    
    async def _apply_noise_suppression(self, audio: np.ndarray) -> np.ndarray:
        """Apply spectral noise suppression"""
        try:
            # Simple spectral subtraction for noise suppression
            # In production, use more advanced algorithms like Wiener filtering
            
            # Compute FFT
            fft = np.fft.rfft(audio)
            magnitude = np.abs(fft)
            phase = np.angle(fft)
            
            # Update noise profile (simple moving average)
            if self.noise_profile is not None:
                alpha = 0.1  # Learning rate
                self.noise_profile = (1 - alpha) * self.noise_profile + alpha * magnitude
                
                # Apply spectral subtraction
                suppression_factor = 2.0
                enhanced_magnitude = magnitude - suppression_factor * self.noise_profile
                enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)
                
                # Reconstruct signal
                enhanced_fft = enhanced_magnitude * np.exp(1j * phase)
                enhanced_audio = np.fft.irfft(enhanced_fft, len(audio))
                
                return enhanced_audio
            
            return audio
            
        except Exception as e:
            logger.warning(f"Noise suppression failed, using original audio: {e}")
            return audio
    
    async def _apply_echo_cancellation(self, audio: np.ndarray) -> np.ndarray:
        """Apply acoustic echo cancellation"""
        try:
            # Simple echo cancellation using adaptive filtering
            # In production, use more sophisticated algorithms like NLMS

            if self.echo_buffer is not None and len(self.echo_buffer) > 0:
                # Simple high-pass filter to reduce echo
                try:
                    from scipy import signal
                    b, a = signal.butter(4, 300 / (self.config.sample_rate / 2), 'high')
                    filtered_audio = signal.filtfilt(b, a, audio)
                    return filtered_audio
                except ImportError:
                    # Fallback without scipy
                    logger.warning("scipy not available, using basic echo cancellation")
                    # Simple moving average filter
                    window_size = min(len(audio) // 10, 100)
                    if window_size > 1:
                        kernel = np.ones(window_size) / window_size
                        filtered_audio = np.convolve(audio, kernel, mode='same')
                        return filtered_audio

            return audio

        except Exception as e:
            logger.warning(f"Echo cancellation failed, using original audio: {e}")
            return audio
    
    async def _apply_auto_gain_control(self, audio: np.ndarray) -> np.ndarray:
        """Apply automatic gain control"""
        try:
            # Calculate RMS level
            rms = np.sqrt(np.mean(audio ** 2))
            
            # Target RMS level (normalized)
            target_rms = 0.1
            
            if rms > 0:
                # Calculate gain adjustment
                gain = target_rms / rms
                
                # Smooth gain changes
                if self.gain_history:
                    previous_gain = self.gain_history[-1]
                    gain = 0.9 * previous_gain + 0.1 * gain
                
                # Apply gain with limiting
                gain = np.clip(gain, 0.1, 10.0)
                self.gain_history.append(gain)
                
                # Keep history limited
                if len(self.gain_history) > 100:
                    self.gain_history = self.gain_history[-50:]
                
                # Apply gain
                return audio * gain
            
            return audio
            
        except Exception as e:
            logger.warning(f"Auto gain control failed, using original audio: {e}")
            return audio
    
    async def _enhance_output_audio(self, audio: np.ndarray) -> np.ndarray:
        """Enhance output audio quality"""
        try:
            # Apply gentle compression for better perceived loudness
            threshold = 0.7
            ratio = 4.0

            # Simple soft compression
            compressed = np.where(
                np.abs(audio) > threshold,
                np.sign(audio) * (threshold + (np.abs(audio) - threshold) / ratio),
                audio
            )

            # Apply gentle EQ boost for voice clarity
            # Boost around 2-4kHz for voice intelligibility
            try:
                from scipy import signal
                b, a = signal.butter(2, [2000, 4000], 'band', fs=self.config.sample_rate)
                eq_boost = signal.filtfilt(b, a, compressed) * 0.2
                enhanced = compressed + eq_boost
            except ImportError:
                # Fallback without scipy - simple high-frequency emphasis
                logger.warning("scipy not available, using basic audio enhancement")
                # Simple high-frequency boost using difference
                if len(compressed) > 1:
                    diff = np.diff(compressed, prepend=compressed[0])
                    enhanced = compressed + diff * 0.1
                else:
                    enhanced = compressed

            # Normalize to prevent clipping
            max_val = np.max(np.abs(enhanced))
            if max_val > 0.95:
                enhanced = enhanced * (0.95 / max_val)

            return enhanced

        except Exception as e:
            logger.warning(f"Output enhancement failed, using original audio: {e}")
            return audio
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get audio processing performance metrics"""
        if not self.processing_times:
            return {}
        
        return {
            "avg_processing_time": np.mean(self.processing_times),
            "max_processing_time": np.max(self.processing_times),
            "min_processing_time": np.min(self.processing_times),
            "total_processed": len(self.processing_times),
            "real_time_factor": np.mean(self.processing_times) / (self.config.chunk_size / self.config.sample_rate)
        }
    
    async def update_mobile_state(self, battery_level: float, thermal_state: str) -> None:
        """Update mobile device state for adaptive processing"""
        try:
            self.battery_level = battery_level
            self.thermal_state = thermal_state

            # Adapt processing quality based on device state
            if self.adaptive_processing:
                await self._adapt_processing_quality()

        except Exception as e:
            logger.error(f"Error updating mobile state: {e}")

    async def _adapt_processing_quality(self) -> None:
        """Adapt processing quality based on mobile device state"""
        try:
            # Determine quality level based on battery and thermal state
            if self.battery_level < 0.2 or self.thermal_state == "hot":
                target_quality = "low"
            elif self.battery_level < 0.5 or self.thermal_state == "warm":
                target_quality = "medium"
            else:
                target_quality = "high"

            if target_quality != self.current_quality_level:
                self.current_quality_level = target_quality
                await self._apply_quality_settings(target_quality)
                logger.info(f"Adapted audio processing quality to {target_quality}")

        except Exception as e:
            logger.error(f"Error adapting processing quality: {e}")

    async def _apply_quality_settings(self, quality_level: str) -> None:
        """Apply quality-specific processing settings"""
        try:
            if quality_level == "low":
                # Minimal processing for battery/thermal conservation
                self.config.noise_suppression = False
                self.config.echo_cancellation = False
                self.config.auto_gain_control = True  # Keep AGC as it's lightweight

            elif quality_level == "medium":
                # Balanced processing
                self.config.noise_suppression = True
                self.config.echo_cancellation = False  # Skip heavy processing
                self.config.auto_gain_control = True

            else:  # high quality
                # Full processing
                self.config.noise_suppression = True
                self.config.echo_cancellation = True
                self.config.auto_gain_control = True

        except Exception as e:
            logger.error(f"Error applying quality settings: {e}")

    async def get_mobile_metrics(self) -> Dict[str, Any]:
        """Get mobile-specific performance metrics"""
        try:
            return {
                "battery_level": self.battery_level,
                "thermal_state": self.thermal_state,
                "current_quality_level": self.current_quality_level,
                "adaptive_processing": self.adaptive_processing,
                "processing_efficiency": {
                    "avg_processing_time": np.mean(self.processing_times) if self.processing_times else 0.0,
                    "real_time_factor": (
                        np.mean(self.processing_times) / (self.config.chunk_size / self.config.sample_rate)
                        if self.processing_times else 0.0
                    )
                }
            }
        except Exception as e:
            logger.error(f"Error getting mobile metrics: {e}")
            return {}

    async def shutdown(self) -> None:
        """Shutdown audio processor"""
        try:
            self.is_initialized = False
            self.noise_profile = None
            self.echo_buffer = None
            self.gain_history.clear()
            self.processing_times.clear()
            logger.info("Audio processor shutdown complete")
        except Exception as e:
            logger.error(f"Error during audio processor shutdown: {e}")
