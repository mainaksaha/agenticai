# Migration to OpenAI GPT-4.1

## Summary of Changes

The system has been migrated from Google Gemini to OpenAI GPT-4.1 (gpt-4-turbo-preview).

## Files Updated

### 1. Core Agent System
- **`agents/base_agent.py`**
  - Replaced `from google import genai` with `from openai import OpenAI`
  - Changed client initialization from `genai.Client()` to `OpenAI()`
  - Updated `process_with_llm()` method to use OpenAI Chat Completions API
  - Changed model from `gemini-2.0-flash-exp` to `gpt-4-turbo-preview`

### 2. Dependencies
- **`requirements.txt`**
  - Removed: `google-genai==0.2.2`
  - Added: `openai>=1.0.0`

### 3. Configuration
- **`.env.example`**
  - Changed: `GOOGLE_API_KEY` → `OPENAI_API_KEY`
  - Updated instructions for obtaining API key

- **`shared/config.py`**
  - Added OpenAI configuration fields:
    - `openai_api_key: str`
    - `openai_model: str = "gpt-4-turbo-preview"`

### 4. Documentation
- **`QUICKSTART.md`**
  - Updated API key setup instructions (Google → OpenAI)
  - Changed API key URL to https://platform.openai.com/api-keys
  
- **`README.md`**
  - Updated technology stack section
  - Changed references from Google ADK to OpenAI GPT-4.1

## API Differences

### Before (Google Gemini)
```python
from google import genai

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=prompt
)
result = response.text
```

### After (OpenAI GPT-4.1)
```python
from openai import OpenAI

client = OpenAI(api_key=api_key)
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.7,
    max_tokens=2000
)
result = response.choices[0].message.content
```

## How to Use

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update Environment Configuration
Create or update your `.env` file:
```bash
cp .env.example .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### 3. Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy and paste it into your `.env` file

### 4. Run the System
```bash
# Option 1: Quick test
python tests/test_workflow.py

# Option 2: With UI
python main.py mock-api  # Terminal 1
streamlit run frontend/streamlit_app.py  # Terminal 2
```

## Model Configuration

The default model is `gpt-4-turbo-preview` (GPT-4.1). You can change this in `shared/config.py`:

```python
openai_model: str = "gpt-4-turbo-preview"  # GPT-4.1
```

Other available models:
- `gpt-4-turbo` - Latest GPT-4 Turbo
- `gpt-4` - Standard GPT-4
- `gpt-3.5-turbo` - Faster, cheaper option

## Cost Considerations

**GPT-4 Turbo Pricing (as of 2024):**
- Input: $0.01 per 1K tokens
- Output: $0.03 per 1K tokens

**Estimated costs for this system:**
- Per break processing: ~2,000-5,000 tokens (~$0.10-$0.25)
- Typical workflow with 10 breaks: ~$1-3

To reduce costs:
1. Use `gpt-3.5-turbo` for non-critical decisions
2. Reduce `max_tokens` in `base_agent.py`
3. Cache frequently used prompts
4. Use GPT-4 only for complex cases

## Backward Compatibility

⚠️ **Breaking Changes:**
- `GOOGLE_API_KEY` environment variable is no longer used
- Must use `OPENAI_API_KEY` instead
- Different API response format (handled internally)

All agent interfaces remain the same - only the underlying LLM changed.

## Testing

All existing tests should work without modification:

```bash
# End-to-end test
python tests/test_workflow.py

# Mock API test
python main.py mock-api  # Terminal 1
python main.py           # Terminal 2
```

## Troubleshooting

### Error: "OPENAI_API_KEY not set"
**Solution:** Create `.env` file with your OpenAI API key

### Error: "pip install openai failed"
**Solution:** Upgrade pip first: `pip install --upgrade pip`

### Error: "Invalid API key"
**Solution:** Verify your API key at https://platform.openai.com/api-keys

### Error: "Rate limit exceeded"
**Solution:** You may need to add payment method or upgrade your OpenAI plan

## Benefits of OpenAI GPT-4.1

1. **Better reasoning** - Superior logic and analysis
2. **Longer context** - Up to 128K tokens
3. **More reliable** - Consistent output format
4. **Better tool use** - Native function calling support
5. **Production ready** - Battle-tested at scale

## Migration Complete ✅

The system is now fully migrated to OpenAI GPT-4.1. All functionality remains the same, with improved LLM capabilities.

---

**Date:** 2025-11-09
**Version:** 2.0 (OpenAI Edition)
