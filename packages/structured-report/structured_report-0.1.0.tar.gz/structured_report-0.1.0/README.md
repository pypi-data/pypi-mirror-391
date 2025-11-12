# Deep Thinking Report API - MVP

A streamlined API that transforms text into structured thought models for learning and reflection. Built with FastAPI and supports multiple LLM providers.

## Features

- **POST /v1/report/insight**: Generate structured analysis from text
- **Dual Model Support**:
  - **OpenAI GPT-4o-mini**: Paid model with higher reasoning capabilities
  - **DeepSeek**: Free model with good performance
- **Depth Levels**: Support for light (1), standard (2), and deep (3) analysis
- **Structured Output**: Consistent JSON response format
- **Docker Support**: Easy deployment with Docker
- **Simplified Architecture**: Clean 134-line codebase for easy maintenance

## Installation

### Option 1: Install from PyPI
```bash
pip install structured-report
```

Run the server:
```bash
structured-report
```

Or run programmatically:
```python
from structured_report.main import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Option 2: Run from source

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd Report_API
   ```

2. **Configure environment:**
   ```bash
   # Create .env file with your API keys
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "DEEPSEEK_API_KEY=your_deepseek_api_key_here" >> .env
   ```

   Get API keys from:
   - **OpenAI**: https://platform.openai.com/api-keys
   - **DeepSeek**: https://platform.deepseek.com/

3. **Run with Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Test the API:**
   ```bash
   curl -X POST "http://localhost:8000/v1/report/insight" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "The future of AI will be dominated by general intelligence systems that can learn and adapt like humans.",
       "model": "deepseek",
       "depth_level": 2
     }'
   ```

## API Usage

### Authentication

This API requires an API Key for all requests. Get your API Key first:

**Get API Key:**
```bash
curl -X POST "http://localhost:8000/api-keys" \
  -H "Content-Type: application/json" \
  -d '{"name": "your-name", "email": "your-email@example.com"}'
```

**Use API Key in requests:**
```bash
curl -X POST "http://localhost:8000/v1/report/insight" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"content": "your text", "model": "deepseek", "depth_level": 2}'
```

### Endpoint: POST /v1/report/insight

**Request:**
```json
{
  "content": "Your text content here",
  "model": "openai",  // or "deepseek"
  "depth_level": 2    // 1=light, 2=standard, 3=deep
}
```

**Model Options:**
- `"openai"`: GPT-4o-mini (paid, higher reasoning quality)
- `"deepseek"`: DeepSeek Chat (free, good performance)

**Response:**
```json
{
  "core_claim": "Extracted main thesis",
  "supporting_arguments": [
    {
      "claim": "Supporting point",
      "evidence": "Evidence from text",
      "logic_type": "Type of reasoning"
    }
  ],
  "assumptions": ["Implicit assumptions"],
  "speaker_position": {
    "role": "Speaker's role",
    "potential_bias": "Potential biases"
  },
  "my_evaluation": "[user will fill]",
  "personal_impact": "[user will fill]",
  "meta_principle": "Transferable principle",
  "falsifiability": ["Conditions where claim fails"],
  "keywords": [
    {
      "term": "Key term",
      "definition": "Definition"
    }
  ],
  "related_insights": ["Related concepts"],
  "meta_questions": ["Questions for further thinking"]
}
```

## Development

**Run locally:**
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

**API Documentation:**
Visit `http://localhost:8000/docs` for interactive API documentation.

## Architecture

**Clean single-file design** with 134 lines of code:
- `app.py`: Complete FastAPI application with Pydantic models
- Supports both OpenAI and DeepSeek models
- Simplified prompt engineering and JSON parsing
- Docker-ready deployment

## MVP Limitations

- Basic error handling
- Simple API Key authentication (no user accounts)
- No rate limiting per API key
- No caching
- No advanced features (batch processing, web UI)

## Next Steps (Future Versions)

- User authentication & API keys
- Rate limiting and quotas
- Response caching
- Web UI interface
- Batch processing
- Advanced prompt engineering
- Knowledge graph visualization
