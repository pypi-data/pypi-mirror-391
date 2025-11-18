# API Key Setup Guide

## For Testing (No API Key Required)

**Good news!** You can run all tests without an OpenAI API key.

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# All tests use mocked responses - no API calls!
```

The tests use `unittest.mock` to simulate API responses, so they:
- ✅ Run without API keys
- ✅ Cost nothing
- ✅ Work offline
- ✅ Are fast and reproducible

## For Running the Application (API Key Required)

To actually use the AI Scientist system, you need an OpenAI API key.

### Step 1: Get an API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-...`)

### Step 2: Configure the Key

**Option A: Environment Variable (Recommended)**
```bash
# Create .env file in project root
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**Option B: System Environment Variable**
```bash
# For macOS/Linux (add to ~/.bashrc or ~/.zshrc)
export OPENAI_API_KEY="sk-your-key-here"

# For Windows
setx OPENAI_API_KEY "sk-your-key-here"
```

### Step 3: Verify Setup

```python
# Test if key is loaded
python -c "from config.settings import OPENAI_API_KEY; print('✅ API key loaded')"
```

### Step 4: Run the Application

```bash
# Web UI
python main.py

# CLI mode
python main.py -m cli
```

## Cost Considerations

OpenAI API usage is pay-per-use
For test purposes, could choose cheaper models.


**Budget tip:** Set usage limits in OpenAI dashboard

## Troubleshooting

### "OpenAI API key not found"
- Check `.env` file exists in project root
- Verify key starts with `sk-`
- Try loading with: `python -c "from config.settings import OPENAI_API_KEY; print(OPENAI_API_KEY)"`

### "Invalid API key"
- Key may be revoked - create new one
- Check for extra spaces/quotes
- Verify account has billing set up

### "Rate limit exceeded"
- OpenAI has usage limits
- Wait a few minutes
- Consider upgrading your OpenAI tier

### Tests fail with "No API key"
- Tests shouldn't need API key!
- Make sure you have `pytest` and `pytest-mock` installed
- Check that tests use `@patch` decorators

## Alternative: Use Local Models

Don't want to use OpenAI? The code can be adapted to use:
- **Ollama** (local open-source models)
- **Anthropic Claude**
- **Azure OpenAI**
- **Any OpenAI-compatible API**

Modify `core/llm_client.py` to use your preferred provider.

## Security Best Practices

⚠️ **Never:**
- Commit API keys to Git
- Share keys publicly
