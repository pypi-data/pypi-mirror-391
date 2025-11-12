from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
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
app = FastAPI(title="Deep Thinking Report API")

# 简单的API Key存储（生产环境建议使用数据库）
API_KEYS = set()

# 安全验证器
security = HTTPBearer(auto_error=False)

# 限流配置
limiter = Limiter(key_func=get_remote_address)

# 添加限流中间件
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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
    # For demo purposes, always return mock response
    return {
        "core_claim": "AI will transform human society and technology fundamentally",
        "supporting_arguments": [
            {
                "claim": "AI can process and analyze vast amounts of data at unprecedented speeds",
                "evidence": "Machine learning algorithms can handle petabytes of data in minutes",
                "logic_type": "factual capability"
            },
            {
                "claim": "AI systems can identify patterns and insights that humans might miss",
                "evidence": "Deep learning networks excel at recognizing complex patterns in data",
                "logic_type": "analytical advantage"
            }
        ],
        "assumptions": [
            "AI development continues at current pace",
            "Society adapts to technological changes",
            "Ethical frameworks guide AI implementation"
        ],
        "speaker_position": {
            "role": "technology analyst",
            "potential_bias": "optimistic about technological progress"
        },
        "my_evaluation": "",
        "personal_impact": "",
        "meta_principle": "Technological revolutions create both opportunities and challenges",
        "falsifiability": [
            "AI development stalls due to technical limitations",
            "Societal resistance prevents widespread adoption",
            "Unforeseen negative consequences outweigh benefits"
        ],
        "keywords": [
            {"term": "artificial intelligence", "definition": "Computer systems capable of performing tasks that typically require human intelligence"},
            {"term": "machine learning", "definition": "AI technique where systems learn from data without explicit programming"},
            {"term": "automation", "definition": "Use of technology to perform tasks with minimal human intervention"}
        ],
        "related_insights": [
            "Impact of automation on employment",
            "Ethical considerations in AI development",
            "Human-AI collaboration models"
        ],
        "meta_questions": [
            "How can we ensure AI benefits all of humanity?",
            "What skills will remain uniquely human?",
            "How do we balance innovation with safety?"
        ]
    }

@app.post("/api-keys", response_model=APIKeyResponse)
@limiter.limit("5/minute")  # API密钥获取限流：每分钟最多5个
async def create_api_key(request_body: APIKeyRequest, request: Request):
    """生成新的API Key"""
    api_key = secrets.token_urlsafe(32)
    API_KEYS.add(api_key)

    return APIKeyResponse(
        api_key=api_key,
        created_at=datetime.now().isoformat()
    )

@app.get("/api-keys/count")
@limiter.limit("10/minute")  # 调试接口限流：每分钟最多10次
async def get_api_keys_count(request: Request):
    """获取当前API Key数量（调试用）"""
    return {"total_api_keys": len(API_KEYS)}

@app.post("/v1/report/insight", response_model=InsightResponse)
@limiter.limit("10/minute")  # 主要API接口限流：每分钟最多10次分析请求
async def generate_insight(
    request_body: InsightRequest,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    if not request_body.content.strip():
        raise HTTPException(400, "Content required")
    if request_body.model not in ["openai", "deepseek"]:
        raise HTTPException(400, "Invalid model")
    if request_body.depth_level not in [1, 2, 3]:
        raise HTTPException(400, "Invalid depth")

    try:
        prompt = get_prompt(request_body.content, request_body.depth_level)
        result = await call_api(request_body.model, prompt)

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

@app.get("/rate-limits")
async def get_rate_limits():
    """获取当前限流配置信息"""
    return {
        "create_api_key": "5/minute",
        "get_api_keys_count": "10/minute",
        "generate_insight": "10/minute",
        "note": "Rate limits are per IP address"
    }

def start_server():
    """CLI入口点"""
    import uvicorn
    uvicorn.run("structured_report.main:app", host="0.0.0.0", port=8000, reload=True)
