# 🔄 smart-selfhealing-rbfw

Self-healing test automation powered by AI 🤖

![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Robot Framework](https://img.shields.io/badge/Robot%20Framework-7.3.2%2B-blue)

---

## 🌟 Features

- **🔧 Automatic Locator Healing** - Automatically fixes broken locators in real-time
- **🧠 LLM-Powered Intelligence** - Uses GPT, Claude, Gemini, or local LLMs (Ollama) for smart locator generation
- **👁️ Vision Support** - Optional screenshot analysis for better accuracy
- **📚 Multi-Library Support** - Works with SeleniumLibrary, Browser Library (Playwright), and AppiumLibrary
- **📊 Detailed Reports** - Beautiful HTML reports showing all fixed locators
- **🎯 Zero Code Changes** - Just add the listener to your test suite
- **🔒 Secure** - All API keys stored in environment variables

---

## 📦 Installation

```bash
pip install smart-selfhealing-rbfw
```

---

## 🚀 Quick Start

### 1. Basic Setup

Add the `SelfHealing` library to your Robot Framework test:

```robotframework
*** Settings ***
Library    SelfHealing    ai_locator_llm=True
```

### 2. Configure Environment Variables

Set up your LLM provider (choose one):

#### Option A: OpenAI (GPT)
```bash
export LLM_API_KEY=your-openai-api-key
export LOCATOR_AI_MODEL=gpt-4o-mini
```

#### Option B: Google Gemini
```bash
export GEMINI_API_KEY=your-gemini-api-key
export LOCATOR_AI_MODEL=gemini/gemini-1.5-flash
```

#### Option C: Local Ollama (Free!)
```bash
export LLM_API_BASE=http://localhost:11434
export LOCATOR_AI_MODEL=ollama_chat/llama3.1
```

### 3. Run Your Tests

```bash
robot tests/
```

That's it! 🎉 The library will automatically heal broken locators and generate a report.

---

## 📖 Usage Examples

### Example 1: Browser Library (Playwright)

```robotframework
*** Settings ***
Library    Browser    timeout=5s
Library    SelfHealing    ai_locator_llm=True

Suite Setup      New Browser    chromium    headless=False
Test Setup       New Context    viewport={'width': 1280, 'height': 720}
Test Teardown    Close Context
Suite Teardown   Close Browser

*** Test Cases ***
Login Test
    New Page    https://example.com/login
    Fill Text    id=username    testuser
    Fill Text    id=password    testpass123
    Click        id=login-button
    Get Text     css=.welcome-message    *=    Welcome
```

### Example 2: SeleniumLibrary

```robotframework
*** Settings ***
Library    SeleniumLibrary    timeout=5s
Library    SelfHealing    ai_locator_llm=True

Suite Setup      Open Browser    https://example.com    chrome
Suite Teardown   Close All Browsers

*** Test Cases ***
Search Product
    Input Text       id=search-box       laptop
    Click Element    id=search-button
    Wait Until Page Contains    Search Results
```

### Example 3: With Vision Support (Recommended for Complex UIs)

```robotframework
*** Settings ***
Library    SelfHealing
...    ai_locator_llm=True
...    ai_locator_visual=True

*** Test Cases ***
Complex UI Test
    # Vision mode captures screenshots to help LLM understand the page better
    Click Element    id=dynamic-button
```

---

## ⚙️ Configuration Options

### Library Import Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ai_locator_llm` | bool | `True` | Enable AI-powered locator healing using LLM |
| `ai_locator_visual` | bool | `False` | Enable screenshot analysis (requires vision-capable model) |
| `ai_locator_database` | bool | `False` | Store healed locators in database for reuse |
| `ai_locator_database_file` | str | `"locator_db.json"` | Path to locator database file |

**Note:** Healing always runs in realtime mode (fixes locators immediately when they fail).

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `LLM_API_KEY` | **Yes*** | API key for LLM provider (OpenAI, etc.) | `sk-...` |
| `GEMINI_API_KEY` | **Yes*** | API key for Google Gemini | `AIza...` |
| `LOCATOR_AI_MODEL` | **Yes** | Model for generating locators (core healing) | `gpt-4o-mini`, `gemini/gemini-1.5-flash` |
| `LOCATOR_AI_MODEL` | **Optional** | Model for text analysis (visual healing only) | `gpt-4o-mini`, `gemini/gemini-1.5-flash` |
| `VISUAL_AI_MODEL` | **Optional** | Model with vision capability (visual healing only) | `gpt-4o`, `gemini/gemini-1.5-pro` |
| `LLM_API_BASE` | No | Custom API endpoint | `http://localhost:11434` (Ollama) |

*Either `LLM_API_KEY` or `GEMINI_API_KEY` required, depending on provider.

**⚠️ Configuration Validation:** 
- When AI features are enabled, the library validates required environment variables at startup
- Missing critical configurations trigger warnings in the log file and console
- `LOCATOR_AI_MODEL` is only required when `ai_locator_visual=True`

---

## 🧠 Supported LLM Providers

This library uses [LiteLLM](https://docs.litellm.ai) for LLM integration, supporting 100+ providers:

### Popular Choices

| Provider | Model Example | Vision Support | Cost |
|----------|--------------|----------------|------|
| **OpenAI** | `gpt-4o-mini`, `gpt-4o` | ✅ Yes | 💰 Paid |
| **Google Gemini** | `gemini/gemini-1.5-flash`, `gemini/gemini-1.5-pro` | ✅ Yes | 💰 Paid / Free tier |
| **Anthropic Claude** | `claude-3-5-sonnet-20241022` | ✅ Yes | 💰 Paid |
| **Ollama (Local)** | `ollama_chat/llama3.1`, `ollama_chat/llama3.2-vision` | ✅ Yes | 🆓 Free |

See full provider list: https://docs.litellm.ai/docs/providers

---

## 📊 Self-Healing Reports

After test execution, open the **SELF-HEALING** button in your Robot Framework report:

- **Fixed Locators** - All healed locators with before/after comparison
- **Success Rate** - Percentage of successful healings
- **Recommendations** - Suggested permanent fixes for your test code

---

## 🔒 Security Best Practices

⚠️ **Never commit API keys to version control!**

### Recommended Setup

1. **Use environment variables:**
```bash
export LLM_API_KEY=your-secret-key
```

2. **Or use `.env` file:**
```bash
# .env (add to .gitignore!)
LLM_API_KEY=your-secret-key
LOCATOR_AI_MODEL=gpt-4o-mini
```

3. **Load in your test:**
```robotframework
*** Settings ***
Library    SelfHealing    ai_locator_llm=True
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. "LOCATOR_AI_MODEL not set" Error
**Solution:** Set the environment variable:
```bash
export LOCATOR_AI_MODEL=gpt-4o-mini
```

#### 2. Authentication Error
**Solution:** Verify your API key is correct:
```bash
export LLM_API_KEY=your-actual-api-key
```

#### 3. Healing Not Working
**Solution:** Ensure library is imported with healing enabled:
```robotframework
Library    SelfHealing    ai_locator_llm=True
```

#### 4. Vision Mode Fails
**Solution:** Make sure your model supports vision:
- ✅ Works: `gpt-4o`, `gemini-1.5-pro`, `claude-3-5-sonnet`
- ❌ Won't work: `gpt-3.5-turbo`, `gemini-flash-latest`

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Hieu La**
- Email: hieuld@smartosc.com
- Company: SmartOSC

---

## 🙏 Acknowledgments

- Robot Framework community
- LiteLLM for unified LLM integration
- All contributors and users

---

## 📚 Related Resources

- [Robot Framework Documentation](https://robotframework.org/)
- [SeleniumLibrary](https://github.com/robotframework/SeleniumLibrary)
- [Browser Library (Playwright)](https://github.com/MarketSquare/robotframework-browser)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [GitHub Repository](https://github.com/hieuld/smart-selfhealing-rbfw)

---

Made with ❤️ by Hieu La
