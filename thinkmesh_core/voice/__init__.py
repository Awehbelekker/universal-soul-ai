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
from .audio_processor import AudioProcessor
from .voice_session import VoiceSession
from .providers import (
    ElevenLabsTTSProvider,
    DeepgramSTTProvider, 
    SileroVADProvider
)

__all__ = [
    "VoiceInterface",
    "AudioProcessor", 
    "VoiceSession",
    "ElevenLabsTTSProvider",
    "DeepgramSTTProvider",
    "SileroVADProvider"
]
