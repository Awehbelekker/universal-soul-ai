# 🔑 API Setup Guide for Multi-Modal AI Integration

## 📋 Overview

This guide walks you through setting up API accounts and configuring the enhanced Universal Soul AI system with multi-modal AI capabilities.

## 🎯 Required API Providers

### **1. OpenAI GPT-4 Vision** (Primary - Highest Priority)
- **Purpose**: Semantic UI understanding and element analysis
- **Cost**: ~$50/month for 100 beta users
- **Accuracy**: 95%+ for UI element detection

### **2. Anthropic Claude Vision** (Secondary - High Priority)  
- **Purpose**: Contextual workflow analysis and strategic reasoning
- **Cost**: ~$30/month for 100 beta users
- **Strength**: Excellent contextual understanding

### **3. Google AI Gemini Pro Vision** (Tertiary - Medium Priority)
- **Purpose**: Multi-modal processing and comprehensive analysis
- **Cost**: ~$25/month for 100 beta users
- **Strength**: Multi-modal capabilities

## 🚀 Step-by-Step API Setup

### **Step 1: OpenAI GPT-4 Vision Setup**

#### **Account Creation:**
1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Sign up for an account (requires payment method)
3. Verify your email and phone number
4. Add payment method (credit card required)

#### **API Key Generation:**
1. Navigate to **API Keys** section
2. Click **"Create new secret key"**
3. Name it: `Universal-Soul-AI-Production`
4. Copy the key immediately (you won't see it again)
5. Store securely in password manager

#### **Usage Limits & Billing:**
```bash
# Recommended settings for beta testing:
Rate Limit: 100 requests/minute
Monthly Budget: $100 (with alerts at $75)
Usage Tracking: Enabled
```

#### **Test API Connection:**
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4-vision-preview",
    "messages": [{"role": "user", "content": "Test connection"}],
    "max_tokens": 10
  }'
```

### **Step 2: Anthropic Claude Vision Setup**

#### **Account Creation:**
1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up for an account
3. Verify email address
4. Complete account verification process

#### **API Key Generation:**
1. Navigate to **API Keys** section
2. Click **"Create Key"**
3. Name it: `Universal-Soul-AI-Claude`
4. Copy the key and store securely

#### **Usage Configuration:**
```bash
# Recommended settings:
Rate Limit: 50 requests/minute
Monthly Budget: $75 (with alerts at $50)
Model Access: Claude-3-Sonnet (with vision)
```

#### **Test API Connection:**
```bash
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Test connection"}]
  }'
```

### **Step 3: Google AI Gemini Pro Setup**

#### **Account Creation:**
1. Go to [https://aistudio.google.com/](https://aistudio.google.com/)
2. Sign in with Google account
3. Accept terms of service
4. Enable billing if required

#### **API Key Generation:**
1. Navigate to **API Keys** section
2. Click **"Create API Key"**
3. Name it: `Universal-Soul-AI-Gemini`
4. Copy the key and store securely

#### **Usage Configuration:**
```bash
# Recommended settings:
Rate Limit: 60 requests/minute
Monthly Budget: $50 (with alerts at $35)
Model Access: Gemini-Pro-Vision
```

#### **Test API Connection:**
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Test connection"}]}]
  }'
```

## ⚙️ Configuration Setup

### **Step 4: Configure API Keys in Universal Soul AI**

#### **Create Production API Keys File:**
```bash
# Navigate to project directory
cd /path/to/universal-soul-ai

# Copy template to production file
cp android_overlay/api_keys_template.env android_overlay/api_keys.env

# Edit with your actual API keys
nano android_overlay/api_keys.env
```

#### **Production Configuration:**
```env
# =============================================================================
# PRODUCTION API KEYS - Universal Soul AI Multi-Modal Integration
# =============================================================================

# Voice Processing (Existing)
ELEVENLABS_API_KEY=your_elevenlabs_key_here
DEEPGRAM_API_KEY=your_deepgram_key_here

# Multi-Modal AI Integration (New)
OPENAI_API_KEY=sk-proj-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
GOOGLE_AI_API_KEY=your_google_ai_key_here

# Multi-Modal Configuration
MULTIMODAL_AI_ENABLED=true
PREFERRED_VISION_PROVIDER=gpt4_vision
ENABLE_PREDICTIVE_AUTOMATION=true
ENABLE_ADAPTIVE_LEARNING=true
MULTIMODAL_FALLBACK_LOCAL=true

# Performance Settings
LOW_LATENCY_MODE=true
MULTIMODAL_CACHE_ENABLED=true

# Cost Control
MAX_DAILY_API_CALLS=1000
COST_ALERT_THRESHOLD=50
USAGE_MONITORING_ENABLED=true
```

### **Step 5: Validate Configuration**

#### **Run Configuration Test:**
```bash
# Test all API connections
python examples/multimodal_ai_demo.py

# Expected output:
# ✅ GPT-4 Vision provider initialized
# ✅ Claude Vision provider initialized  
# ✅ Gemini Pro Vision provider initialized
# ✅ Multi-Modal AI Demo initialized successfully
```

#### **Validate API Functionality:**
```bash
# Test individual providers
python -c "
import asyncio
from thinkmesh_core.ai_providers import MultiModalAIProvider

async def test():
    provider = MultiModalAIProvider({'OPENAI_API_KEY': 'your_key'})
    await provider.initialize()
    print('✅ All providers initialized successfully')

asyncio.run(test())
"
```

## 🔒 Security Best Practices

### **API Key Security:**

1. **Never commit API keys to version control**
   ```bash
   # Add to .gitignore
   echo "android_overlay/api_keys.env" >> .gitignore
   echo "*.env" >> .gitignore
   ```

2. **Use environment variables in production**
   ```bash
   export OPENAI_API_KEY="your_key_here"
   export ANTHROPIC_API_KEY="your_key_here"
   export GOOGLE_AI_API_KEY="your_key_here"
   ```

3. **Implement key rotation schedule**
   - Rotate keys every 90 days
   - Monitor for unusual usage patterns
   - Set up billing alerts

### **Access Control:**
```bash
# Restrict file permissions
chmod 600 android_overlay/api_keys.env

# Only allow owner read/write access
ls -la android_overlay/api_keys.env
# Should show: -rw------- 1 user user
```

## 📊 Cost Monitoring Setup

### **Billing Alerts Configuration:**

#### **OpenAI Billing Alerts:**
1. Go to **Billing** → **Usage limits**
2. Set **Hard limit**: $100/month
3. Set **Soft limit**: $75/month (email alert)
4. Enable **Usage notifications**

#### **Anthropic Billing Alerts:**
1. Go to **Billing** → **Usage**
2. Set **Monthly budget**: $75
3. Enable **Email alerts** at 80% usage

#### **Google AI Billing Alerts:**
1. Go to **Billing** → **Budgets & alerts**
2. Create budget: $50/month
3. Set alert thresholds: 50%, 80%, 100%

### **Usage Monitoring Script:**
```python
# Create monitoring script
cat > scripts/monitor_api_usage.py << 'EOF'
#!/usr/bin/env python3
"""Monitor API usage and costs"""

import asyncio
import logging
from datetime import datetime
from thinkmesh_core.ai_providers import MultiModalAIProvider

async def monitor_usage():
    provider = MultiModalAIProvider()
    await provider.initialize()
    
    report = await provider.get_performance_report()
    
    print(f"📊 API Usage Report - {datetime.now()}")
    print(f"Available providers: {len(report['available_providers'])}")
    print(f"Total API calls today: {report.get('total_calls', 0)}")
    print(f"Estimated cost today: ${report.get('estimated_cost', 0):.2f}")

if __name__ == "__main__":
    asyncio.run(monitor_usage())
EOF

chmod +x scripts/monitor_api_usage.py
```

## ✅ Validation Checklist

### **Pre-Deployment Validation:**

- [ ] **OpenAI GPT-4 Vision API key working**
- [ ] **Anthropic Claude Vision API key working**  
- [ ] **Google AI Gemini Pro API key working**
- [ ] **API keys securely stored and not in version control**
- [ ] **Billing alerts configured for all providers**
- [ ] **Usage monitoring enabled**
- [ ] **Multi-modal demo running successfully**
- [ ] **Fallback to local processing working**
- [ ] **Cost controls implemented**
- [ ] **Security best practices followed**

### **Post-Setup Testing:**

```bash
# Run comprehensive validation
python examples/multimodal_ai_demo.py

# Expected results:
# ✅ All API providers initialized
# ✅ Screen analysis working with 90%+ confidence
# ✅ Predictive automation planning functional
# ✅ Adaptive learning system operational
# ✅ Cost monitoring active
```

## 🚨 Troubleshooting

### **Common Issues:**

#### **API Key Authentication Errors:**
```bash
# Check API key format
echo $OPENAI_API_KEY | grep -E "^sk-proj-"  # Should match
echo $ANTHROPIC_API_KEY | grep -E "^sk-ant-"  # Should match

# Test individual API calls
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

#### **Rate Limit Errors:**
```bash
# Check current usage
python scripts/monitor_api_usage.py

# Adjust rate limits in configuration
MULTIMODAL_MAX_REQUESTS_PER_MINUTE=50
```

#### **Cost Overruns:**
```bash
# Enable strict cost controls
COST_ALERT_THRESHOLD=25  # Lower threshold
MAX_DAILY_API_CALLS=500  # Reduce limits
```

## 📞 Support Contacts

### **API Provider Support:**
- **OpenAI**: [https://help.openai.com/](https://help.openai.com/)
- **Anthropic**: [https://support.anthropic.com/](https://support.anthropic.com/)
- **Google AI**: [https://support.google.com/](https://support.google.com/)

### **Emergency Procedures:**
1. **Disable APIs immediately**: Set `MULTIMODAL_AI_ENABLED=false`
2. **Revoke API keys** from provider dashboards
3. **Check billing** for unexpected charges
4. **Contact provider support** if needed

---

**🎉 Once all APIs are configured and validated, proceed to the next phase: Enhanced Build Pipeline Integration!**
