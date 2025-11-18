"""
Utility functions for the Segmentation Agent.
"""

import logging
from typing import Dict, Any, Optional, List
from sfn_db_query_builder import fetch_column_name_datatype


logger = logging.getLogger(__name__)


def get_customer_column_name(sf_column_name: str, mappings: Dict[str, Any]) -> str:
    """
    Get customer-friendly column name from StepFunction column name using mappings.
    
    Args:
        sf_column_name: StepFunction/internal column name
        mappings: Dictionary mapping StepFunction column names to customer column names
                  Format: {SF_COLUMN_NAME: customer_column_name}
    
    Returns:
        Customer column name if mapping exists, otherwise returns original name
    """
    if not mappings:
        return sf_column_name
    
    # Direct mapping lookup
    if sf_column_name in mappings:
        return mappings[sf_column_name]
    
    # Case-insensitive lookup
    sf_lower = sf_column_name.lower()
    for sf_key, customer_name in mappings.items():
        if sf_key.lower() == sf_lower:
            return customer_name
    
    return sf_column_name


def get_sf_column_name(customer_column_name: str, mappings: Dict[str, Any]) -> str:
    """
    Get StepFunction column name from customer column name using reverse mapping.
    
    Args:
        customer_column_name: Customer-friendly column name
        mappings: Dictionary mapping StepFunction column names to customer column names
    
    Returns:
        StepFunction column name if reverse mapping exists, otherwise returns original name
    """
    if not mappings:
        return customer_column_name
    
    # Reverse lookup: find SF column name that maps to this customer name
    for sf_key, customer_name in mappings.items():
        if customer_name == customer_column_name:
            return sf_key
    
    # Case-insensitive reverse lookup
    customer_lower = customer_column_name.lower()
    for sf_key, customer_name in mappings.items():
        if customer_name.lower() == customer_lower:
            return sf_key
    
    return customer_column_name


def get_table_metadata(
    data_store: str,
    db_session: Any,
    schema_name: str,
    table_name: str
) -> Dict[str, Any]:
    """
    Fetch table metadata using sfn_db_query_builder.
    
    Args:
        data_store: Data store type (e.g., 'snowflake')
        db_session: Database session/connection
        schema_name: Schema name
        table_name: Table name
        
    Returns:
        Dictionary with table metadata including columns and data types
    """
    try:
        columns = fetch_column_name_datatype(
            data_store,
            db_session,
            schema_name,
            table_name
        )
        
        return {
            "schema": schema_name,
            "table_name": table_name,
            "columns": columns,
            "column_count": len(columns) if columns else 0
        }
    except Exception as e:
        logger.error(f"Error fetching table metadata: {e}")
        return {
            "schema": schema_name,
            "table_name": table_name,
            "columns": [],
            "column_count": 0,
            "error": str(e)
        }


def get_final_table_name(
    experiment_type: str,
    project_name: str
) -> tuple[str, str]:
    """
    Get the final table name and schema based on experiment type.
    
    Args:
        experiment_type: Type of experiment (e.g., 'classification', 'regression')
        project_name: Project name
        
    Returns:
        Tuple of (table_name, schema_name)
    """
    EXPERIMENT_FINAL_TABLE_NAME = "experiment_final_dataset"
    source_table = f"{experiment_type}_{EXPERIMENT_FINAL_TABLE_NAME}"
    source_schema = f"{project_name.lower()}_operations"
    
    return source_table, source_schema


def extract_segment_count(user_text: str) -> int:
    """
    Try to extract segment count from user text.
    This is a simple heuristic - LLM will do better analysis.
    
    Args:
        user_text: User's natural language input
        
    Returns:
        Estimated segment count (default: 1)
    """
    text_lower = user_text.lower()
    
    # Look for explicit numbers
    if "3 segments" in text_lower or "three segments" in text_lower:
        return 3
    if "2 segments" in text_lower or "two segments" in text_lower:
        return 2
    if "multiple segments" in text_lower or "several segments" in text_lower:
        return 2  # Default to 2 for multiple
    
    # Look for list patterns (e.g., "segment 1: ..., segment 2: ...")
    if "segment 1" in text_lower and "segment 2" in text_lower:
        return 2
    if "segment 1" in text_lower and "segment 2" in text_lower and "segment 3" in text_lower:
        return 3
    
    return 1  # Default to single segment


def validate_sql_syntax(query: str) -> tuple[bool, Optional[str]]:
    """
    Basic SQL syntax validation.
    More comprehensive validation should be done via dry run.
    
    Args:
        query: SQL query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    query_upper = query.upper().strip()
    
    # Basic checks
    if not query_upper.startswith("SELECT"):
        return False, "Query must start with SELECT"
    
    if "FROM" not in query_upper:
        return False, "Query must contain FROM clause"
    
    # Check for dangerous operations (agent shouldn't do these)
    dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE TABLE", "CREATE VIEW"]
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False, f"Query contains prohibited keyword: {keyword}"
    
    return True, None


def format_segment_name(raw_name: str) -> str:
    """
    Format segment name to be valid for use in SQL/dataset names.
    
    Args:
        raw_name: Raw segment name from user/LLM
        
    Returns:
        Formatted segment name
    """
    # Convert to lowercase, replace spaces with underscores
    formatted = raw_name.lower().strip().replace(" ", "_")
    
    # Remove invalid characters
    import re
    formatted = re.sub(r'[^a-z0-9_]', '', formatted)
    
    # Ensure it doesn't start with a number
    if formatted and formatted[0].isdigit():
        formatted = f"segment_{formatted}"
    
    # Ensure it's not empty
    if not formatted:
        formatted = "segment_1"
    
    return formatted

