# African Market OS — MVR API Python Client

Official **Python SDK** for the  
**Minimum Viable Relationships (MVR) API — v2.6.0-enterprise**

This client provides full access to all MVR API endpoints:

### ✔ Scores  
### ✔ Survey aggregation  
### ✔ Trends  
### ✔ Forecasts  
### ✔ Benchmarking  
### ✔ Insights  
### ✔ Policy multi-audit  
### ✔ Stories  
### ✔ Metadata + Usage  
### ✔ Health checks  
### ✔ Session token authentication  

---

## 📦 Installation

You can install directly from PyPI (recommended):

```bash
pip install mvr-api-client

Or install from source:

pip install .

🚀 Quickstart Example

from mvr_api import MVRApiClient, MVRApiConfig

# Create configuration
config = MVRApiConfig(
    license="your-license-key",
    email="you@example.com"
)

# Initialize client
client = MVRApiClient(config)

# Call API
scores = client.get_scores("fintech")
print("MVR Index:", scores.mvr_index)

🧪 Submitting Survey Data

from mvr_api import SurveyAggregateRequest, StakeholderResponse

survey_request = SurveyAggregateRequest(
    stakeholder_responses=[
        StakeholderResponse(
            dimension="Embeddedness",
            scale=4,
            reasons=["Strong community integration"]
        )
    ],
    sector="fintech"
)

result = client.survey_aggregate(survey_request)
print(result.mvr_index)

📈 Trends Example
trends = client.get_trends(sector="fmcg", days=30)
print("Average Index:", trends.average_index)
print("Slope:", trends.slope)

🔮 Forecast Example
from mvr_api import ForecastRequest

forecast = client.forecast(ForecastRequest(
    current_index=0.65,
    velocity=0.02,
    horizon=30
))

print("Projected MVR:", forecast.projected_index)

👥 Entity Comparison
from mvr_api import CompareRequest

comparison = client.compare(CompareRequest(
    a_index=0.72,
    b_index=0.58
))

print("Delta:", comparison.delta)
print("Verdict:", comparison.verdict)

📊 Benchmarks
bench = client.get_benchmark("fintech")
print(bench.benchmark)

♨ Temperature
temp = client.get_temperature()
print(temp.continent_score)

📘 Metadata
meta = client.get_meta()
print(meta.model)

🔐 Session-Based Authentication
# Create session token
session = client.create_session("license-key", "you@example.com")

# Build session-authenticated client
session_client = client.with_session(session.session_token)

scores = session_client.get_scores()
print(scores.mvr_index)

🛡 Error Handling

All API errors raise a structured MVRApiError:

from mvr_api import MVRApiError

try:
    client.get_scores()
except MVRApiError as e:
    print("Error:", e.error_data.error_code)
    print("Message:", e.error_data.message)

📂 Project Structure
mvr-api-py-client/
│
├── setup.py
├── README.md
└── mvr_api/
    ├── __init__.py
    ├── client.py
    └── models.py

📄 License

This SDK is released under the MIT License.

🧬 Attribution
MVR Framework • African Market OS
Creator: Farouk Mark Mukiibi
Framework DOI: 10.5281/zenodo.17310446

🌍 About

The Minimum Viable Relationships (MVR) Framework measures:

Trust

Belonging

Permission

Embeddedness

…to evaluate relational readiness for ventures entering
high-context markets across Africa.

Learn more:https://africanmarketos.com/the-mvr-framework-minimum-viable-relationships/


