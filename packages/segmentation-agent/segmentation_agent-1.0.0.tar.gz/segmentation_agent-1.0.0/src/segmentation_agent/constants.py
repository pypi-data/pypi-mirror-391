"""
Constants and prompt templates for the Segmentation Agent.
"""
from typing import Dict, Any, Optional, List

# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

SYSTEM_PROMPT_INTENT_UNDERSTANDING = """
You are an expert data analyst specializing in dataset segmentation for machine learning.
Your role is to understand user segmentation requirements and translate them into clear business logic.

Given:
- User's natural language segmentation request
- Dataset schema and column metadata
- Column mappings (StepFunction column names → Customer column names)
- Business domain and use case context

Your tasks:
1. Parse the user's intent to identify if they want single or multiple segments
2. For each segment, identify:
   - Segment name/identifier
   - Business understanding in plain language (USE CUSTOMER COLUMN NAMES in explanations)
   - Columns that will be used for segmentation (use StepFunction column names for internal reference)
   - Segmentation logic (filters, conditions, etc.) - describe using customer column names
3. Generate clear, business-friendly explanations for each segment

IMPORTANT: 
- In business_understanding and segmentation_logic descriptions, ALWAYS use customer column names (from mappings)
- This ensures users understand what columns you're referring to
- For identified_columns, use StepFunction column names (for internal processing)
- When describing filters/conditions in plain language, use customer-friendly names

Example:
- If mapping is {"REVENUE": "Total Revenue", "CUSTOMER_ID": "Customer ID"}
- Business understanding should say: "Customers with Total Revenue > 10000"
- Not: "Customers with REVENUE > 10000"
- But identified_columns should be: ["REVENUE", "CUSTOMER_ID"]

Provide outputs in JSON format with confidence scores for each segment.
"""

SYSTEM_PROMPT_SQL_GENERATION = """
You are a highly skilled SQL expert with deep knowledge of SQL syntax and business domain segmentation.

Your role:
- Convert validated business understanding into executable SQL WHERE clauses
- For multiple segments: Generate separate SQL queries for each segment
- Ensure SQL follows best practices for the target database
- Reference only columns that exist in the dataset schema
- Generate queries that are efficient and maintainable
- Each segment query should be independent and executable separately

For multiple segments, provide outputs in JSON format with:
- Array of segment objects, each containing:
  - segment_name: Unique identifier for the segment
  - sql_query: Executable SELECT query with WHERE clause
  - query_explanation: Plain English explanation
  - confidence_score: Confidence in query correctness (0-1)

Important: Generate SELECT queries only. Do NOT include CREATE TABLE or CREATE VIEW statements.
The queries should be ready to be used in CREATE VIEW AS SELECT or CREATE TABLE AS SELECT statements by other services.
"""

SYSTEM_PROMPT_HEALTH_ANALYSIS = """
You are a data quality analyst specializing in ML dataset evaluation.

Analyze the segment data and provide:
- Distribution statistics for key columns
- Target variable analysis (if applicable)
- Temporal patterns (if temporal data exists)
- Entity-based patterns (if entity/ID columns exist)
- Overall health assessment with recommendations

Provide outputs in JSON format with detailed metrics and health scores.
"""

SYSTEM_PROMPT_SQL_REFACTOR = """
You are a SQL expert. Refactor SQL queries to fix errors, but do NOT change the logic, columns, or tables.
Only adjust datatype casts, value formats, or other syntax/formatting issues as required by the error.
Return only the corrected, executable SQL query, no explanation.
"""

# =============================================================================
# USER PROMPT TEMPLATES
# =============================================================================

def format_intent_understanding_prompt(
    user_text: str,
    dataset_metadata: Dict[str, Any],
    business_context: Dict[str, Any],
    use_case: str,
    ml_approach: str,
    mappings: Optional[Dict[str, Any]] = None
) -> str:
    """
    Format the user prompt for intent understanding.
    
    Args:
        user_text: User's natural language segmentation request
        dataset_metadata: Table metadata with columns and data types
        business_context: Business domain and context information
        use_case: Business use case
        ml_approach: ML approach (classification, regression, etc.)
        mappings: Column mappings (StepFunction → Customer column names)
        
    Returns:
        Formatted user prompt
    """
    # Build column information with customer names if mappings exist
    columns_info_list = []
    for col in dataset_metadata.get('columns', []):
        sf_col_name = col.get('column_name', 'unknown')
        data_type = col.get('data_type', 'unknown')
        
        # Get customer column name if mapping exists
        if mappings:
            from .utils import get_customer_column_name
            customer_name = get_customer_column_name(sf_col_name, mappings)
            if customer_name != sf_col_name:
                columns_info_list.append(
                    f"- {customer_name} (internal: {sf_col_name}): {data_type}"
                )
            else:
                columns_info_list.append(f"- {sf_col_name}: {data_type}")
        else:
            columns_info_list.append(f"- {sf_col_name}: {data_type}")
    
    columns_info = "\n".join(columns_info_list)
    
    # Add mappings information if available
    mappings_info = ""
    if mappings:
        mappings_list = [
            f"  - {sf_name} → {customer_name}"
            for sf_name, customer_name in mappings.items()
        ]
        mappings_info = f"\n\nColumn Mappings (StepFunction → Customer Names):\n" + "\n".join(mappings_list)
    
    return f"""
Analyze the following segmentation request and generate business understanding.

User's Segmentation Request:
"{user_text}"

Dataset Information:
- Schema: {dataset_metadata.get('schema', 'unknown')}
- Table: {dataset_metadata.get('table_name', 'unknown')}
- Columns:
{columns_info}{mappings_info}

Business Context:
- Use Case: {use_case}
- ML Approach: {ml_approach}
- Domain: {business_context.get('domain', 'general')}
- Business Description: {business_context.get('description', 'N/A')}

Your task:
1. Determine if this is a single segment or multiple segments request
2. For each segment, provide:
   - segment_name: A clear, descriptive name
   - business_understanding: Plain English explanation using CUSTOMER COLUMN NAMES (from mappings)
   - identified_columns: List of StepFunction column names (for internal processing)
   - segmentation_logic: Description using CUSTOMER COLUMN NAMES (so users understand)
   - confidence_score: Your confidence in understanding this segment (0-1)

IMPORTANT: Use customer column names in business_understanding and segmentation_logic descriptions.
Use StepFunction column names in identified_columns array.

Return valid JSON in this format:
{{
    "segment_count": <number>,
    "segments": [
        {{
            "segment_name": "segment_name",
            "business_understanding": "clear explanation using customer column names",
            "identified_columns": ["SF_COL1", "SF_COL2"],
            "segmentation_logic": "filter description using customer column names",
            "confidence_score": 0.85
        }}
    ]
}}
"""


def format_sql_generation_prompt(
    business_understandings: List[Dict[str, Any]],
    dataset_metadata: Dict[str, Any],
    source_schema: str,
    source_table: str
) -> str:
    """
    Format the user prompt for SQL generation.
    
    Args:
        business_understandings: List of business understanding dictionaries
        dataset_metadata: Table metadata with columns and data types
        source_schema: Source schema name
        source_table: Source table name
        
    Returns:
        Formatted user prompt
    """
    columns_info = "\n".join([
        f"- {col.get('column_name', 'unknown')}: {col.get('data_type', 'unknown')}"
        for col in dataset_metadata.get('columns', [])
    ])
    
    segments_info = "\n".join([
        f"""
Segment {i+1}: {seg.get('segment_name', 'unknown')}
- Business Understanding: {seg.get('business_understanding', 'N/A')}
- Identified Columns: {', '.join(seg.get('identified_columns', []))}
- Segmentation Logic: {seg.get('segmentation_logic', 'N/A')}
"""
        for i, seg in enumerate(business_understandings)
    ])
    
    return f"""
Generate SQL queries for the following segments.

Source Table:
- Schema: {source_schema}
- Table: {source_table}

Available Columns:
{columns_info}

Segments to Generate:
{segments_info}

Your task:
Generate a SELECT query with WHERE clause for each segment. The query should:
1. Select all columns from the source table
2. Apply the appropriate WHERE conditions based on the segmentation logic
3. Be executable independently
4. Follow SQL best practices

Return valid JSON in this format:
{{
    "segment_count": {len(business_understandings)},
    "segments": [
        {{
            "segment_name": "segment_name",
            "sql_query": "SELECT * FROM {source_schema}.{source_table} WHERE ...",
            "query_explanation": "explanation of what the query does",
            "confidence_score": 0.90
        }}
    ]
}}

Important: 
- Use SELECT * FROM {source_schema}.{source_table} as the base
- Only add WHERE clauses for filtering
- Do NOT include CREATE TABLE or CREATE VIEW statements
"""


def format_health_analysis_prompt(
    segment_name: str,
    segment_query: str,
    dataset_metadata: Dict[str, Any],
    target_column: Optional[str] = None
) -> str:
    """
    Format the user prompt for health analysis.
    
    Args:
        segment_name: Name of the segment
        segment_query: SQL query used for the segment
        dataset_metadata: Table metadata
        target_column: Optional target column name
        
    Returns:
        Formatted user prompt
    """
    target_info = f"\n- Target Column: {target_column}" if target_column else "\n- Target Column: Not specified"
    
    return f"""
Analyze the health and quality of the following segment.

Segment Name: {segment_name}
Segment Query: {segment_query}
{target_info}

Dataset Metadata:
- Total Columns: {len(dataset_metadata.get('columns', []))}
- Column Types: {', '.join(set([col.get('data_type', 'unknown') for col in dataset_metadata.get('columns', [])]))}

Your task:
Analyze the segment and provide:
1. Data distribution statistics
2. Target distribution (if target column exists)
3. Temporal distribution (if temporal columns exist)
4. Entity distribution (if entity/ID columns exist)
5. Overall health score (0-1) and assessment (excellent/good/fair/poor)
6. Reasons for the health assessment
7. Recommendations for improvement

Return valid JSON with detailed metrics.
"""


def format_sql_refactor_prompt(
    sql_query: str,
    error: str,
    dataset_metadata: Dict[str, Any]
) -> str:
    """
    Format the user prompt for SQL refactoring.
    
    Args:
        sql_query: The SQL query that failed
        error: Error message from execution
        dataset_metadata: Table metadata
        
    Returns:
        Formatted user prompt
    """
    columns_info = "\n".join([
        f"- {col.get('column_name', 'unknown')}: {col.get('data_type', 'unknown')}"
        for col in dataset_metadata.get('columns', [])
    ])
    
    return f"""
SQL Query:
{sql_query}

Error:
{error}

Available Columns:
{columns_info}

Fix the SQL query to resolve the error. Do NOT change the logic, only fix syntax/formatting issues.
Return only the corrected SQL query, no explanation.
"""

