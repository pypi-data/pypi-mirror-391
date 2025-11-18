from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime


class AttributionObject(BaseModel):
    framework: str = Field(..., example="Minimum Viable Relationships (MVR)")
    creator: str = Field(..., example="Farouk Mark Mukiibi")
    source: str = Field(..., example="African Market OS")
    license: str = Field(..., example="CC BY 4.0 | Commercial Use Licensed")
    doi: str = Field(..., example="10.5281/zenodo.17310446")


class VersionInfo(BaseModel):
    api: str = Field(..., example="2.6.0")
    feature: Optional[str] = None
    method: Optional[str] = None
    model: Optional[str] = None
    mvr_proprietary: bool = Field(..., example=True)


class MVRError(BaseModel):
    ok: bool = Field(..., example=False)
    error: str
    error_code: str
    message: str
    request_id: Optional[str] = None
    limit: Optional[int] = None
    window: Optional[str] = None
    retry_after: Optional[int] = None
    attribution: AttributionObject


class MVRDimension(BaseModel):
    name: str
    score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    threshold_ok: bool
    binding: bool
    evidence_ptrs: List[str] = Field(default_factory=list)


class MVRScoreResponse(BaseModel):
    ok: bool
    mvr_index: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    sector: str
    mvr_dimensions: List[MVRDimension]
    mvr_threshold: bool
    recommendations: List[str]
    version_info: VersionInfo
    attribution: AttributionObject


class StakeholderResponse(BaseModel):
    dimension: str
    scale: int = Field(..., ge=1, le=5)
    reasons: List[str] = Field(default_factory=list)


class SurveyAggregateRequest(BaseModel):
    stakeholder_responses: List[StakeholderResponse]
    sector: Optional[str] = None

    @validator("sector")
    def validate_sector(cls, v):
        valid_sectors = [
            "fmcg", "fintech", "policy",
            "health", "agritech", "retail", "default"
        ]
        if v and v not in valid_sectors:
            raise ValueError(
                f"Sector must be one of: {', '.join(valid_sectors)}"
            )
        return v


class SurveyAggregateResponse(BaseModel):
    ok: bool
    sector: str
    mvr_index: float = Field(..., ge=0, le=1)
    matrix_axes: Dict[str, float]
    insights: List[str]
    recommendations: List[str]
    summary: str
    version_info: VersionInfo
    attribution: AttributionObject


class TrendsResponse(BaseModel):
    ok: bool
    sector: str
    days: int
    average_index: float
    slope: float
    interpretation: str
    version_info: VersionInfo
    attribution: AttributionObject


class ForecastRequest(BaseModel):
    current_index: float = Field(..., ge=0, le=1)
    velocity: float
    horizon: int = Field(default=30, ge=1)


class ForecastResponse(BaseModel):
    ok: bool
    current_index: float = Field(..., ge=0, le=1)
    projected_index: float = Field(..., ge=0, le=1)
    horizon_days: int
    confidence: float = Field(..., ge=0, le=1)
    pmf_projection: str
    version_info: VersionInfo
    attribution: AttributionObject


class CompareRequest(BaseModel):
    a_index: float = Field(..., ge=0, le=1)
    b_index: float = Field(..., ge=0, le=1)


class CompareResponse(BaseModel):
    ok: bool
    delta: float
    verdict: str
    policy_trace: Dict[str, Any]
    version_info: VersionInfo
    attribution: AttributionObject


class BenchmarkResponse(BaseModel):
    ok: bool
    sector: str
    benchmark: Dict[str, Union[int, float]]
    version_info: VersionInfo
    attribution: AttributionObject


class InsightEntity(BaseModel):
    rank: int
    sector: str
    mvr_index: float = Field(..., ge=0, le=1)
    caption: str


class InsightsResponse(BaseModel):
    ok: bool
    sector: str
    top_entities: List[InsightEntity]
    version_info: VersionInfo
    attribution: AttributionObject


class TemperatureResponse(BaseModel):
    ok: bool
    date: str
    continent_score: float = Field(..., ge=0, le=1)
    hottest_sector: str
    coolest_sector: str
    region: str
    sample_size: int
    version_info: VersionInfo
    attribution: AttributionObject


class PolicyAuditResponse(BaseModel):
    ok: bool
    policies_analyzed: int
    compliance_score: float = Field(..., ge=0, le=1)
    recommendations: List[str]
    version_info: VersionInfo
    attribution: AttributionObject


class StoryResponse(BaseModel):
    ok: bool
    story: str
    impact_metrics: Dict[str, float]
    version_info: VersionInfo
    attribution: AttributionObject


class MetaResponse(BaseModel):
    ok: bool
    api_name: str
    version: str
    model: str
    endpoints: List[str]
    limits: Dict[str, int]
    last_model_refresh: Optional[str] = None
    model_fingerprint: Optional[str] = None
    attribution: AttributionObject


class UsageResponse(BaseModel):
    ok: bool
    plan: str
    date: str
    used_today: int
    daily_limit: int
    attribution: AttributionObject


class WhoAmIResponse(BaseModel):
    ok: bool
    api: str
    version: str
    capabilities: List[str]
    author: str
    region: str
    attribution: AttributionObject


class DocsResponse(BaseModel):
    ok: bool
    documentation: str
    endpoints: List[str]
    version_info: VersionInfo
    attribution: AttributionObject


class SessionResponse(BaseModel):
    ok: bool
    session_token: str
    expires_in: int
    expires_at: str
    plan: str
    version_info: VersionInfo
    attribution: AttributionObject


class HealthResponse(BaseModel):
    ok: bool
    service: str
    time: str
    region: str
    performance: str
    security: str
    version: str
    uptime_seconds: int
    features: List[str]
    attribution: AttributionObject


class MVRApiConfig(BaseModel):
    license: str
    email: str
    base_url: str = "https://mvr-api.africanmarketos.workers.dev"
    timeout: int = 30
    max_retries: int = 3
