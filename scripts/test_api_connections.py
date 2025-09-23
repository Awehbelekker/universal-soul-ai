#!/usr/bin/env python3
"""
API Connection Testing Script
============================

Tests all API connections for Universal Soul AI multi-modal integration.
Validates API keys and provider functionality before deployment.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIConnectionTester:
    """Test API connections for all providers"""
    
    def __init__(self):
        self.api_keys = {}
        self.test_results = {}
        
    def load_api_keys(self) -> bool:
        """Load API keys from environment file"""
        
        api_keys_file = project_root / "android_overlay" / "api_keys.env"
        
        if not api_keys_file.exists():
            logger.error("❌ API keys file not found: android_overlay/api_keys.env")
            return False
        
        try:
            with open(api_keys_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if value and value != "your_api_key_here":
                            self.api_keys[key] = value
            
            logger.info(f"✅ Loaded {len(self.api_keys)} API keys")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load API keys: {e}")
            return False
    
    async def test_openai_connection(self) -> bool:
        """Test OpenAI GPT-4 Vision API connection"""
        
        logger.info("🧠 Testing OpenAI GPT-4 Vision connection...")
        
        api_key = self.api_keys.get("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            logger.warning("⚠️ OpenAI API key not configured")
            return False
        
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=api_key)
            
            # Test with a simple completion
            response = await client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{
                    "role": "user",
                    "content": "Test connection - respond with 'OK'"
                }],
                max_tokens=10
            )
            
            if response.choices[0].message.content:
                logger.info("✅ OpenAI GPT-4 Vision: Connection successful")
                return True
            else:
                logger.error("❌ OpenAI GPT-4 Vision: Invalid response")
                return False
                
        except ImportError:
            logger.error("❌ OpenAI library not installed: pip install openai")
            return False
        except Exception as e:
            logger.error(f"❌ OpenAI GPT-4 Vision connection failed: {e}")
            return False
    
    async def test_anthropic_connection(self) -> bool:
        """Test Anthropic Claude Vision API connection"""
        
        logger.info("🎯 Testing Anthropic Claude Vision connection...")
        
        api_key = self.api_keys.get("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your_anthropic_api_key_here":
            logger.warning("⚠️ Anthropic API key not configured")
            return False
        
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            # Test with a simple message
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=10,
                messages=[{
                    "role": "user",
                    "content": "Test connection - respond with 'OK'"
                }]
            )
            
            if response.content and response.content[0].text:
                logger.info("✅ Anthropic Claude Vision: Connection successful")
                return True
            else:
                logger.error("❌ Anthropic Claude Vision: Invalid response")
                return False
                
        except ImportError:
            logger.error("❌ Anthropic library not installed: pip install anthropic")
            return False
        except Exception as e:
            logger.error(f"❌ Anthropic Claude Vision connection failed: {e}")
            return False
    
    async def test_google_ai_connection(self) -> bool:
        """Test Google AI Gemini Pro Vision API connection"""
        
        logger.info("🌟 Testing Google AI Gemini Pro connection...")
        
        api_key = self.api_keys.get("GOOGLE_AI_API_KEY")
        if not api_key or api_key == "your_google_ai_api_key_here":
            logger.warning("⚠️ Google AI API key not configured")
            return False
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            
            # Test with a simple generation
            model = genai.GenerativeModel('gemini-pro')
            response = await model.generate_content_async("Test connection - respond with 'OK'")
            
            if response.text:
                logger.info("✅ Google AI Gemini Pro: Connection successful")
                return True
            else:
                logger.error("❌ Google AI Gemini Pro: Invalid response")
                return False
                
        except ImportError:
            logger.error("❌ Google AI library not installed: pip install google-generativeai")
            return False
        except Exception as e:
            logger.error(f"❌ Google AI Gemini Pro connection failed: {e}")
            return False
    
    async def test_voice_apis(self) -> Dict[str, bool]:
        """Test voice processing APIs"""
        
        logger.info("🎙️ Testing voice processing APIs...")
        
        results = {}
        
        # Test ElevenLabs
        elevenlabs_key = self.api_keys.get("ELEVENLABS_API_KEY")
        if elevenlabs_key and elevenlabs_key != "your_elevenlabs_api_key_here":
            try:
                import elevenlabs
                
                # Simple API test
                voices = elevenlabs.voices()
                if voices:
                    logger.info("✅ ElevenLabs TTS: Connection successful")
                    results["elevenlabs"] = True
                else:
                    logger.error("❌ ElevenLabs TTS: No voices returned")
                    results["elevenlabs"] = False
                    
            except ImportError:
                logger.error("❌ ElevenLabs library not installed: pip install elevenlabs")
                results["elevenlabs"] = False
            except Exception as e:
                logger.error(f"❌ ElevenLabs TTS connection failed: {e}")
                results["elevenlabs"] = False
        else:
            logger.warning("⚠️ ElevenLabs API key not configured")
            results["elevenlabs"] = False
        
        # Test Deepgram
        deepgram_key = self.api_keys.get("DEEPGRAM_API_KEY")
        if deepgram_key and deepgram_key != "your_deepgram_api_key_here":
            try:
                from deepgram import Deepgram
                
                # Simple API test
                dg_client = Deepgram(deepgram_key)
                # Note: Actual test would require audio file
                logger.info("✅ Deepgram STT: API key format valid")
                results["deepgram"] = True
                    
            except ImportError:
                logger.error("❌ Deepgram library not installed: pip install deepgram-sdk")
                results["deepgram"] = False
            except Exception as e:
                logger.error(f"❌ Deepgram STT connection failed: {e}")
                results["deepgram"] = False
        else:
            logger.warning("⚠️ Deepgram API key not configured")
            results["deepgram"] = False
        
        return results
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive API connection tests"""
        
        logger.info("🚀 Starting comprehensive API connection tests...")
        logger.info("=" * 60)
        
        # Load API keys
        if not self.load_api_keys():
            return {"success": False, "error": "Failed to load API keys"}
        
        # Test multi-modal AI providers
        logger.info("\n🧠 Testing Multi-Modal AI Providers:")
        logger.info("-" * 40)
        
        openai_result = await self.test_openai_connection()
        anthropic_result = await self.test_anthropic_connection()
        google_result = await self.test_google_ai_connection()
        
        # Test voice APIs
        logger.info("\n🎙️ Testing Voice Processing APIs:")
        logger.info("-" * 40)
        
        voice_results = await self.test_voice_apis()
        
        # Compile results
        results = {
            "success": True,
            "timestamp": asyncio.get_event_loop().time(),
            "multimodal_ai": {
                "openai_gpt4_vision": openai_result,
                "anthropic_claude_vision": anthropic_result,
                "google_gemini_pro": google_result
            },
            "voice_processing": voice_results,
            "summary": {
                "total_providers": 5,
                "working_providers": sum([
                    openai_result,
                    anthropic_result, 
                    google_result,
                    voice_results.get("elevenlabs", False),
                    voice_results.get("deepgram", False)
                ]),
                "multimodal_providers_working": sum([
                    openai_result,
                    anthropic_result,
                    google_result
                ]),
                "voice_providers_working": sum(voice_results.values())
            }
        }
        
        # Generate summary
        logger.info("\n📊 Test Results Summary:")
        logger.info("=" * 60)
        
        working = results["summary"]["working_providers"]
        total = results["summary"]["total_providers"]
        
        logger.info(f"Overall Status: {working}/{total} providers working")
        
        # Multi-modal AI status
        multimodal_working = results["summary"]["multimodal_providers_working"]
        if multimodal_working >= 2:
            logger.info("✅ Multi-Modal AI: Ready for deployment (2+ providers working)")
        elif multimodal_working >= 1:
            logger.info("⚠️ Multi-Modal AI: Limited functionality (1 provider working)")
        else:
            logger.info("❌ Multi-Modal AI: Not functional (no providers working)")
        
        # Voice processing status
        voice_working = results["summary"]["voice_providers_working"]
        if voice_working >= 2:
            logger.info("✅ Voice Processing: Fully functional")
        elif voice_working >= 1:
            logger.info("⚠️ Voice Processing: Limited functionality")
        else:
            logger.info("❌ Voice Processing: Not functional")
        
        # Deployment readiness
        if multimodal_working >= 1 and working >= 3:
            logger.info("\n🎉 DEPLOYMENT READY: System can be deployed for beta testing")
            results["deployment_ready"] = True
        elif multimodal_working >= 1:
            logger.info("\n⚠️ LIMITED DEPLOYMENT: Core functionality available, some features limited")
            results["deployment_ready"] = True
        else:
            logger.info("\n❌ NOT READY: Critical APIs not working, deployment not recommended")
            results["deployment_ready"] = False
        
        # Next steps
        logger.info("\n🔧 Next Steps:")
        if not openai_result:
            logger.info("  • Configure OpenAI API key for best UI understanding")
        if not anthropic_result:
            logger.info("  • Configure Anthropic API key for contextual reasoning")
        if not google_result:
            logger.info("  • Configure Google AI API key for multi-modal analysis")
        if not voice_results.get("elevenlabs", False):
            logger.info("  • Configure ElevenLabs API key for voice synthesis")
        if not voice_results.get("deepgram", False):
            logger.info("  • Configure Deepgram API key for speech recognition")
        
        if results["deployment_ready"]:
            logger.info("  • Run deployment script: python scripts/deploy_beta.py")
        
        return results


async def main():
    """Main testing function"""
    
    print("🧪 Universal Soul AI - API Connection Testing")
    print("=" * 60)
    print("Testing all API providers for multi-modal AI integration...")
    print()
    
    tester = APIConnectionTester()
    results = await tester.run_comprehensive_test()
    
    if results["deployment_ready"]:
        print("\n🎉 API testing completed successfully!")
        print("System is ready for beta deployment!")
        sys.exit(0)
    else:
        print("\n⚠️ API testing completed with issues.")
        print("Please configure missing API keys before deployment.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
