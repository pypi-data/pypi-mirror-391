"""
Segmentation Agent - Intelligent dataset segmentation for ML workflows.
"""

from .agent import SegmentationAgent
from .config import SegmentationConfig
from .models import (
    AgentInputsRequest,
    SegmentationRequest,
    SegmentationUnderstanding,
    SegmentationQuery,
    SegmentationHealth,
)

# Export utility functions for convenience
from .utils import (
    get_table_metadata,
    get_final_table_name,
    get_customer_column_name,
    get_sf_column_name,
    validate_sql_syntax,
    format_segment_name,
)

__version__ = "1.0.0"
__all__ = [
    "SegmentationAgent",
    "SegmentationConfig",
    "AgentInputsRequest",
    "SegmentationRequest",
    "SegmentationUnderstanding",
    "SegmentationQuery",
    "SegmentationHealth",
    # Utility functions
    "get_table_metadata",
    "get_final_table_name",
    "get_customer_column_name",
    "get_sf_column_name",
    "validate_sql_syntax",
    "format_segment_name",
]

