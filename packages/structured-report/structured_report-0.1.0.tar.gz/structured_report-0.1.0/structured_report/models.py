from pydantic import BaseModel
from typing import List

class InsightRequest(BaseModel):
    content: str
    model: str = "openai"
    depth_level: int = 2

class SupportingArgument(BaseModel):
    claim: str
    evidence: str
    logic_type: str

class Keyword(BaseModel):
    term: str
    definition: str

class SpeakerPosition(BaseModel):
    role: str
    potential_bias: str

class InsightResponse(BaseModel):
    core_claim: str
    supporting_arguments: List[SupportingArgument]
    assumptions: List[str]
    speaker_position: SpeakerPosition
    my_evaluation: str = "[user will fill]"
    personal_impact: str = "[user will fill]"
    meta_principle: str
    falsifiability: List[str]
    keywords: List[Keyword]
    related_insights: List[str]
    meta_questions: List[str]

class APIKeyRequest(BaseModel):
    name: str
    email: str = None

class APIKeyResponse(BaseModel):
    api_key: str
    created_at: str
