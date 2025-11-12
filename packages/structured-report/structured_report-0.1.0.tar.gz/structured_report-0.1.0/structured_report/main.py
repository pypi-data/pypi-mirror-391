from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import httpx
import json
import os
import secrets
from datetime import datetime
from dotenv import load_dotenv
import openai
from .models import InsightRequest, InsightResponse, APIKeyRequest, APIKeyResponse

load_dotenv()
app = FastAPI()

# 简单的API Key存储（生产环境建议使用数据库）
API_KEYS = set()

# 安全验证器
security = HTTPBearer(auto_error=False)

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证API Key"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required. Get one at /api-keys"
        )

    if credentials.credentials not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    return credentials.credentials

def get_prompt(content: str, depth_level: int) -> str:
    prompt = f"""
Analyze this text and output ONLY valid JSON: {content}

{{
  "core_claim": "main thesis",
  "supporting_arguments": [
    {{"claim": "argument", "evidence": "supporting text", "logic_type": "reasoning type"}}
  ],
  "assumptions": ["underlying assumptions"],
  "speaker_position": {{
    "role": "speaker's role",
    "potential_bias": "possible biases"
  }},
  "my_evaluation": "[user will fill]",
  "personal_impact": "[user will fill]",
  "meta_principle": "transferable principle",
  "falsifiability": ["conditions where claim fails"],
  "keywords": [
    {{"term": "keyword", "definition": "definition"}}
  ],
  "related_insights": ["related concepts"],
  "meta_questions": ["questions for further thinking"]
}}
"""
    if depth_level == 1:
        return prompt + "Keep analysis brief."
    elif depth_level == 3:
        return prompt + "Provide detailed analysis."
    return prompt

async def call_api(model: str, prompt: str) -> dict:
    if model == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
    else:  # deepseek
        api_key = os.getenv("DEEPSEEK_API_KEY")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
            )
            content = response.json()["choices"][0]["message"]["content"]

    # Clean and parse JSON
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]
    return json.loads(content.strip())

@app.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(request: APIKeyRequest):
    """生成新的API Key"""
    api_key = secrets.token_urlsafe(32)
    API_KEYS.add(api_key)

    return APIKeyResponse(
        api_key=api_key,
        created_at=datetime.now().isoformat()
    )

@app.get("/api-keys/count")
async def get_api_keys_count():
    """获取当前API Key数量（调试用）"""
    return {"total_api_keys": len(API_KEYS)}

@app.post("/v1/report/insight", response_model=InsightResponse)
async def generate_insight(
    request: InsightRequest,
    api_key: str = Depends(verify_api_key)
):
    if not request.content.strip():
        raise HTTPException(400, "Content required")
    if request.model not in ["openai", "deepseek"]:
        raise HTTPException(400, "Invalid model")
    if request.depth_level not in [1, 2, 3]:
        raise HTTPException(400, "Invalid depth")

    try:
        prompt = get_prompt(request.content, request.depth_level)
        result = await call_api(request.model, prompt)

        # Validate required fields
        required = ["core_claim", "supporting_arguments", "assumptions",
                   "speaker_position", "meta_principle", "falsifiability",
                   "keywords", "related_insights", "meta_questions"]
        for field in required:
            if field not in result:
                raise HTTPException(500, f"Missing {field}")

        return InsightResponse(**result)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def start_server():
    """CLI入口点"""
    import uvicorn
    uvicorn.run("structured_report.main:app", host="0.0.0.0", port=8000, reload=True)
