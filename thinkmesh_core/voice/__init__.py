"""
Voice Interface Module for ThinkMesh AI
======================================

Premium voice processing with ElevenLabs TTS, Deepgram STT, and Silero VAD
for the highest quality mobile voice experience.

Features:
- Studio-quality text-to-speech with ElevenLabs
- Real-time speech-to-text with Deepgram
- Advanced voice activity detection with Silero
- Mobile-optimized audio processing
- Real-time noise suppression and echo cancellation
- Privacy-first local processing options

Copyright (c) 2025 ThinkMesh AI Systems
"""

from .voice_interface import VoiceInterface
from .audio_processor import AudioProcessor, AudioConfig
from .voice_session import VoiceSession, VoiceSessionConfig
from .providers import (
    ElevenLabsTTSProvider,
    DeepgramSTTProvider,
    SileroVADProvider
)
# Import VoiceConfig from config module for convenience
from ..config import VoiceConfig

__all__ = [
    "VoiceInterface",
    "VoiceConfig",
    "AudioProcessor",
    "AudioConfig",
    "VoiceSession",
    "VoiceSessionConfig",
    "ElevenLabsTTSProvider",
    "DeepgramSTTProvider",
    "SileroVADProvider"
]
