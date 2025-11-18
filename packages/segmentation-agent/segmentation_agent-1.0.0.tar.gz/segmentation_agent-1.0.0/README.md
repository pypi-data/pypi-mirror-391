# Segmentation Agent

AI-powered dataset segmentation agent for machine learning workflows. This agent intelligently segments ML-ready datasets according to business problem context, analyzes segments, and produces evaluation metrics.

## Overview

The Segmentation Agent provides three independent phases for dataset segmentation:

1. **Understanding & Validation**: Parse user intent and generate business understanding
2. **SQL Generation**: Generate executable SQL queries from validated understanding  
3. **Health Analysis**: Analyze segment data and generate health metrics

## Features

- **Natural Language Processing**: Understand segmentation requests in plain English
- **Multi-Segment Support**: Generate multiple segments in one pass, each creating independent datasets
- **SQL Query Generation**: Generate executable SQL queries (SELECT with WHERE clauses)
- **Dry Run Validation**: Validate SQL queries before execution
- **Health Metrics**: Comprehensive segment health analysis with distribution statistics
- **Stateless Design**: All methods are independent and can be called separately
- **Business Understanding**: Generate human-readable explanations for each segment

## Installation

```bash
pip install segmentation-agent
```

Or from source:

```bash
git clone https://github.com/stepfnAI/segmentation_agent.git
cd segmentation_agent
pip install -e .
```

## Quick Start

### Phase 1: Understanding Segmentation Intent

```python
from segmentation_agent import SegmentationAgent, AgentInputsRequest
from segmentation_agent.utils import get_table_metadata, get_final_table_name

# Initialize agent
agent = SegmentationAgent()

# Prepare request
request = AgentInputsRequest(
    conn=db_connection,
    auth_service_base_url="",
    project_name="my_project",
    schema="my_schema",
    table_name="my_table",
    mappings={},
    use_case="churn_prediction",
    ml_approach="binary_classification",
    experiment_type="classification"
)

# Get table metadata
experiment_type = "classification"
source_table, source_schema = get_final_table_name(experiment_type, "my_project")
dataset_metadata = get_table_metadata(
    data_store="snowflake",
    db_session=db_connection,
    schema_name=source_schema,
    table_name=source_table
)

# Understand segmentation intent
user_text = "create 3 segments: high-value customers (revenue > 10000), medium-value (revenue 5000-10000), low-value (revenue < 5000)"

understanding = agent.understand_segmentation_intent(
    user_text=user_text,
    request=request,
    dataset_metadata=dataset_metadata
)

print(understanding.to_dict())
```

### Phase 2: Generate SQL Queries

```python
# After user validates/confirms the understanding, generate SQL queries
business_understandings = [
    seg.to_dict() for seg in understanding.segments
]

queries = agent.generate_segmentation_query(
    business_understandings=business_understandings,
    request=request,
    dataset_metadata=dataset_metadata
)

print(queries.to_dict())
```

### Phase 3: Analyze Segment Health

```python
# After executing queries and getting segment data, analyze health
segment_queries = [
    {"segment_name": seg.segment_name, "sql_query": seg.sql_query}
    for seg in queries.segments
]

health = agent.analyze_multiple_segment_health(
    conn=db_connection,
    segment_queries=segment_queries,
    dataset_metadata=dataset_metadata,
    target_column="churn_target"
)

print(health.to_dict())
```

## Configuration

The agent can be configured via environment variables or a config file:

```bash
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4o-mini
export LLM_API_KEY=your_api_key
```

Or programmatically:

```python
from segmentation_agent import SegmentationConfig, SegmentationAgent

config = SegmentationConfig(
    ai_provider="openai",
    model_name="gpt-4o-mini",
    temperature=0.3,
    max_tokens=4000
)

agent = SegmentationAgent(config=config)
```

## Architecture

### Agent Responsibilities

**What the Agent DOES:**
- Generate business understanding from natural language
- Generate SQL queries (SELECT with WHERE clauses)
- Validate SQL syntax (dry run)
- Analyze segment health metrics
- Generate business reasons for segment value

**What the Agent DOES NOT DO:**
- Create tables/views (handled by other services)
- Manage database connections (passed in via request)
- Maintain session state (stateless design)
- Handle destination-specific details (handled by other services)

### Stateless Design

The agent is designed to be stateless:
- Each phase is a separate method call
- No session state maintained between calls
- User validation happens externally
- Agent generates output → User modifies → Agent regenerates with new input

## Multi-Segment Support

The agent supports creating multiple segments in one pass:

```python
user_text = """
create 3 segments:
1. High-value customers: revenue > 10000
2. Medium-value customers: revenue between 5000 and 10000
3. Low-value customers: revenue < 5000
"""

understanding = agent.understand_segmentation_intent(...)
# Returns understanding for all 3 segments

queries = agent.generate_segmentation_query(...)
# Returns 3 separate SQL queries

health = agent.analyze_multiple_segment_health(...)
# Returns health metrics for all 3 segments with comparative analysis
```

Each segment:
- Has its own SQL query
- Creates a separate dataset
- Can be used for independent experiments
- Has individual health metrics

## Output Formats

### Phase 1 Output (Business Understanding)

```json
{
    "status": "understanding_generated",
    "segment_count": 3,
    "segments": [
        {
            "segment_name": "high_value_customers",
            "business_understanding": "Segment for customers with revenue > 10000",
            "identified_columns": ["customer_id", "revenue"],
            "segmentation_logic": "Filter where revenue > 10000",
            "confidence_score": 0.90
        }
    ],
    "requires_confirmation": true
}
```

### Phase 2 Output (SQL Queries)

```json
{
    "status": "queries_generated",
    "segment_count": 3,
    "segments": [
        {
            "segment_name": "high_value_customers",
            "sql_query": "SELECT * FROM schema.table WHERE revenue > 10000",
            "query_explanation": "This query segments data by high revenue customers",
            "dry_run_status": "valid",
            "estimated_row_count": 1000,
            "confidence_score": 0.90
        }
    ]
}
```

### Phase 3 Output (Health Analysis)

```json
{
    "status": "success",
    "segment_count": 3,
    "segments": [
        {
            "segment_name": "high_value_customers",
            "segment_query": "SELECT * FROM ...",
            "execution_details": {...},
            "dataset_name": "high_value_customers_dataset",
            "experiment_ready": true,
            "segment_health": {
                "row_count": 1000,
                "health_score": 0.85,
                "health_assessment": "good"
            },
            "reasons": [...],
            "recommendations": [...]
        }
    ],
    "comparative_analysis": {...}
}
```

## Dependencies

- `sfn-blueprint`: Base framework and LLM handling
- `sfn-db-query-builder`: Database metadata utilities
- `sqlalchemy`: Database connection and query execution
- `pandas`: Data analysis (for health metrics)
- `pydantic`: Data validation and settings

## License

MIT

## Contributing

Contributions are welcome! Please see the contributing guidelines for more information.

