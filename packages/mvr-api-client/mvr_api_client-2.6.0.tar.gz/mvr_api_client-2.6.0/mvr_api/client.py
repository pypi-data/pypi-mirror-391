import time
import requests
from typing import Optional, Dict, Any
from .models import (
    MVRApiConfig, MVRScoreResponse, SurveyAggregateRequest,
    SurveyAggregateResponse, TrendsResponse, ForecastRequest,
    ForecastResponse, CompareRequest, CompareResponse,
    BenchmarkResponse, InsightsResponse, TemperatureResponse,
    PolicyAuditResponse, StoryResponse, MetaResponse,
    UsageResponse, WhoAmIResponse, DocsResponse, SessionResponse,
    HealthResponse, MVRError, AttributionObject
)


class MVRApiError(Exception):
    """Base exception for MVR API errors."""
    def __init__(self, error_data: MVRError):
        self.error_data = error_data
        super().__init__(f"{error_data.error_code}: {error_data.message}")


class MVRApiClient:
    """Main MVR API client using License + Email authentication."""

    def __init__(self, config: MVRApiConfig):
        self.config = config

        # Persistent session
        self.session = requests.Session()
        self.session.headers.update({
            "x-mvr-license": config.license,
            "x-buyer-email": config.email,
            "Content-Type": "application/json",
            "User-Agent": "mvr-api-py-client/2.6.0"
        })

        self.base_url = config.base_url
        self.max_retries = config.max_retries
        self.timeout = config.timeout

    # ------------------------------------------------------------
    # INTERNAL REQUEST WRAPPER
    # ------------------------------------------------------------
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Low-level HTTP request with retry + rate limit handling."""

        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs
                )

                data = response.json()

                # -------------------------
                # Successful Response
                # -------------------------
                if response.status_code == 200:
                    return data

                # -------------------------
                # Rate Limited (429)
                # -------------------------
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    if attempt < self.max_retries:
                        time.sleep(retry_after)
                        continue
                    raise MVRApiError(MVRError(**data))

                # -------------------------
                # Other API Errors
                # -------------------------
                raise MVRApiError(MVRError(**data))

            except requests.exceptions.RequestException as e:
                # Network errors (timeouts, connection drops)
                if attempt == self.max_retries:
                    raise MVRApiError(MVRError(
                        ok=False,
                        error="NETWORK_ERROR",
                        error_code="NETWORK_ERROR",
                        message=str(e),
                        attribution=AttributionObject(
                            framework="Minimum Viable Relationships (MVR)",
                            creator="Farouk Mark Mukiibi",
                            source="African Market OS",
                            license="CC BY 4.0 | Commercial Use Licensed",
                            doi="10.5281/zenodo.17310446"
                        )
                    ))
                time.sleep(2 ** attempt)  # exponential retry

    # ------------------------------------------------------------
    # SCORES + SURVEY
    # ------------------------------------------------------------
    def get_scores(self, sector: Optional[str] = None) -> MVRScoreResponse:
        """GET /v1/scores"""
        params: Dict[str, Any] = {}
        if sector:
            params["sector"] = sector

        data = self._request("GET", "/v1/scores", params=params)
        return MVRScoreResponse(**data)

    def survey_aggregate(self, request: SurveyAggregateRequest) -> SurveyAggregateResponse:
        """POST /v1/survey-aggregate"""
        data = self._request("POST", "/v1/survey-aggregate", json=request.dict())
        return SurveyAggregateResponse(**data)

    # ------------------------------------------------------------
    # INTELLIGENCE: TRENDS, FORECAST, COMPARE
    # ------------------------------------------------------------
    def get_trends(
        self,
        sector: Optional[str] = None,
        days: Optional[int] = None
    ) -> TrendsResponse:
        """GET /v1/trends"""
        params: Dict[str, Any] = {}
        if sector:
            params["sector"] = sector
        if days is not None:
            params["days"] = days

        data = self._request("GET", "/v1/trends", params=params)
        return TrendsResponse(**data)

    def forecast(self, request: ForecastRequest) -> ForecastResponse:
        """POST /v1/forecast"""
        data = self._request("POST", "/v1/forecast", json=request.dict())
        return ForecastResponse(**data)

    def compare(self, request: CompareRequest) -> CompareResponse:
        """POST /v1/compare"""
        data = self._request("POST", "/v1/compare", json=request.dict())
        return CompareResponse(**data)

    # ------------------------------------------------------------
    # INTELLIGENCE: BENCHMARK, INSIGHTS, TEMPERATURE
    # ------------------------------------------------------------
    def get_benchmark(self, sector: Optional[str] = None) -> BenchmarkResponse:
        """GET /v1/benchmark"""
        params: Dict[str, Any] = {}
        if sector:
            params["sector"] = sector

        data = self._request("GET", "/v1/benchmark", params=params)
        return BenchmarkResponse(**data)

    def get_insights(self, sector: Optional[str] = None) -> InsightsResponse:
        """GET /v1/insights"""
        params: Dict[str, Any] = {}
        if sector:
            params["sector"] = sector

        data = self._request("GET", "/v1/insights", params=params)
        return InsightsResponse(**data)

    def get_temperature(self) -> TemperatureResponse:
        """GET /v1/temperature"""
        data = self._request("GET", "/v1/temperature")
        return TemperatureResponse(**data)

    # ------------------------------------------------------------
    # INTELLIGENCE: POLICY + STORY
    # ------------------------------------------------------------
    def get_policy_multi(self) -> PolicyAuditResponse:
        """GET /v1/policy_multi"""
        data = self._request("GET", "/v1/policy_multi")
        return PolicyAuditResponse(**data)

    def post_policy_multi(self) -> PolicyAuditResponse:
        """POST /v1/policy_multi"""
        data = self._request("POST", "/v1/policy_multi")
        return PolicyAuditResponse(**data)

    def get_story(self) -> StoryResponse:
        """GET /v1/story"""
        data = self._request("GET", "/v1/story")
        return StoryResponse(**data)

    def post_story(self) -> StoryResponse:
        """POST /v1/story"""
        data = self._request("POST", "/v1/story")
        return StoryResponse(**data)

    # ------------------------------------------------------------
    # UTILITIES
    # ------------------------------------------------------------
    def get_meta(self) -> MetaResponse:
        """GET /v1/meta"""
        data = self._request("GET", "/v1/meta")
        return MetaResponse(**data)

    def get_usage(self) -> UsageResponse:
        """GET /v1/usage"""
        data = self._request("GET", "/v1/usage")
        return UsageResponse(**data)

    def whoami(self) -> WhoAmIResponse:
        """GET /v1/whoami"""
        data = self._request("GET", "/v1/whoami")
        return WhoAmIResponse(**data)

    def get_docs(self) -> DocsResponse:
        """GET /v1/docs"""
        data = self._request("GET", "/v1/docs")
        return DocsResponse(**data)

    def create_session(self, license: str, email: str) -> SessionResponse:
        """POST /v1/session/new"""
        payload = {"license": license, "email": email}
        data = self._request("POST", "/v1/session/new", json=payload)
        return SessionResponse(**data)

    def health(self) -> HealthResponse:
        """GET /v1/health"""
        data = self._request("GET", "/v1/health")
        return HealthResponse(**data)

    # ------------------------------------------------------------
    # SESSION-BASED CLIENT FACTORY
    # ------------------------------------------------------------
    def with_session(self, session_token: str) -> "SessionMVRApiClient":
        """Return a SessionMVRApiClient using x-mvr-session auth."""
        return SessionMVRApiClient(
            base_url=self.base_url,
            session_token=session_token,
            timeout=self.timeout
        )


# ============================================================
# SESSION-BASED CLIENT (x-mvr-session)
# ============================================================
class SessionMVRApiClient:
    """MVR API client using session-token authentication."""

    def __init__(self, base_url: str, session_token: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session_token = session_token

        self.session = requests.Session()
        self.session.headers.update({
            "x-mvr-session": session_token,
            "Content-Type": "application/json",
            "User-Agent": "mvr-api-py-client/2.6.0"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Internal request handler"""
        url = f"{self.base_url}{endpoint}"

        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        data = response.json()

        if response.status_code != 200:
            raise MVRApiError(MVRError(**data))

        return data

    # --------------------------------------------------------
    # Session-auth GET/POST endpoints
    # --------------------------------------------------------
    def get_scores(self, sector: Optional[str] = None) -> MVRScoreResponse:
        params = {"sector": sector} if sector else {}
        data = self._request("GET", "/v1/scores", params=params)
        return MVRScoreResponse(**data)

    def get_trends(self, sector: Optional[str] = None, days: Optional[int] = None) -> TrendsResponse:
        params = {}
        if sector:
            params["sector"] = sector
        if days:
            params["days"] = days

        data = self._request("GET", "/v1/trends", params=params)
        return TrendsResponse(**data)

    def forecast(self, request: ForecastRequest) -> ForecastResponse:
        data = self._request("POST", "/v1/forecast", json=request.dict())
        return ForecastResponse(**data)

    def compare(self, request: CompareRequest) -> CompareResponse:
        data = self._request("POST", "/v1/compare", json=request.dict())
        return CompareResponse(**data)

    def get_benchmark(self, sector: Optional[str] = None) -> BenchmarkResponse:
        params = {"sector": sector} if sector else {}
        data = self._request("GET", "/v1/benchmark", params=params)
        return BenchmarkResponse(**data)

    def get_insights(self, sector: Optional[str] = None) -> InsightsResponse:
        params = {"sector": sector} if sector else {}
        data = self._request("GET", "/v1/insights", params=params)
        return InsightsResponse(**data)

    def get_temperature(self) -> TemperatureResponse:
        data = self._request("GET", "/v1/temperature")
        return TemperatureResponse(**data)

    def get_policy_multi(self) -> PolicyAuditResponse:
        data = self._request("GET", "/v1/policy_multi")
        return PolicyAuditResponse(**data)

    def post_policy_multi(self) -> PolicyAuditResponse:
        data = self._request("POST", "/v1/policy_multi")
        return PolicyAuditResponse(**data)

    def get_story(self) -> StoryResponse:
        data = self._request("GET", "/v1/story")
        return StoryResponse(**data)

    def post_story(self) -> StoryResponse:
        data = self._request("POST", "/v1/story")
        return StoryResponse(**data)

    def get_meta(self) -> MetaResponse:
        data = self._request("GET", "/v1/meta")
        return MetaResponse(**data)

    def get_usage(self) -> UsageResponse:
        data = self._request("GET", "/v1/usage")
        return UsageResponse(**data)

    def whoami(self) -> WhoAmIResponse:
        data = self._request("GET", "/v1/whoami")
        return WhoAmIResponse(**data)

    def get_docs(self) -> DocsResponse:
        data = self._request("GET", "/v1/docs")
        return DocsResponse(**data)

    def health(self) -> HealthResponse:
        data = self._request("GET", "/v1/health")
        return HealthResponse(**data)

