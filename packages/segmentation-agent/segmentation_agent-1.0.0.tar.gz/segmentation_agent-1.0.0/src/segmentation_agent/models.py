"""
Data models for the Segmentation Agent.
"""

from typing import List, Dict, Any, Optional, TypedDict
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# Reuse AgentInputsRequest pattern from target_synthesis_agent
class AgentInputsRequest(TypedDict, total=False):
    """Input parameters for segmentation agent (following target_synthesis_agent pattern)."""
    conn: Any  # Database connection
    auth_service_base_url: str
    project_name: str
    schema: Optional[str] = None
    table_name: str
    mappings: Dict[str, Any]
    use_case: str
    ml_approach: str
    experiment_type: Optional[str] = None


@dataclass
class SegmentUnderstanding:
    """Business understanding for a single segment."""
    segment_name: str
    business_understanding: str
    identified_columns: List[str]
    segmentation_logic: str
    confidence_score: float = 0.0


@dataclass
class SegmentationUnderstanding:
    """Complete business understanding result (Phase 1 output)."""
    status: str
    segment_count: int
    segments: List[SegmentUnderstanding]
    requires_confirmation: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "segment_count": self.segment_count,
            "segments": [
                {
                    "segment_name": seg.segment_name,
                    "business_understanding": seg.business_understanding,
                    "identified_columns": seg.identified_columns,
                    "segmentation_logic": seg.segmentation_logic,
                    "confidence_score": seg.confidence_score
                }
                for seg in self.segments
            ],
            "requires_confirmation": self.requires_confirmation
        }


@dataclass
class SegmentQuery:
    """SQL query for a single segment."""
    segment_name: str
    sql_query: str
    query_explanation: str
    dry_run_status: str = "pending"
    estimated_row_count: Optional[int] = None
    confidence_score: float = 0.0


@dataclass
class SegmentationQuery:
    """Complete SQL query generation result (Phase 2 output)."""
    status: str
    segment_count: int
    segments: List[SegmentQuery]
    total_estimated_rows: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "status": self.status,
            "segment_count": self.segment_count,
            "segments": [
                {
                    "segment_name": seg.segment_name,
                    "sql_query": seg.sql_query,
                    "query_explanation": seg.query_explanation,
                    "dry_run_status": seg.dry_run_status,
                    "estimated_row_count": seg.estimated_row_count,
                    "confidence_score": seg.confidence_score
                }
                for seg in self.segments
            ]
        }
        if self.total_estimated_rows is not None:
            result["total_estimated_rows"] = self.total_estimated_rows
        return result


@dataclass
class SegmentHealthMetrics:
    """Health metrics for a single segment."""
    row_count: int
    data_distribution: Dict[str, Any] = field(default_factory=dict)
    target_distribution: Optional[Dict[str, Any]] = None
    temporal_distribution: Optional[Dict[str, Any]] = None
    entity_distribution: Optional[Dict[str, Any]] = None
    health_score: float = 0.0
    health_assessment: str = "unknown"  # excellent, good, fair, poor


@dataclass
class SegmentHealth:
    """Complete health analysis for a single segment."""
    segment_name: str
    segment_query: str
    execution_details: Dict[str, Any]
    dataset_name: str
    experiment_ready: bool
    segment_health: SegmentHealthMetrics
    reasons: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ComparativeAnalysis:
    """Comparative analysis across multiple segments."""
    total_rows_across_segments: int
    best_health_score: float
    segment_with_best_health: str
    recommended_segment_for_modeling: str
    health_comparison: Dict[str, float]


@dataclass
class SegmentationHealth:
    """Complete health analysis result (Phase 3 output)."""
    status: str
    segment_count: int
    total_segments_processed: int
    segments: List[SegmentHealth]
    comparative_analysis: Optional[ComparativeAnalysis] = None
    experiment_configuration: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "status": self.status,
            "segment_count": self.segment_count,
            "total_segments_processed": self.total_segments_processed,
            "segments": [
                {
                    "segment_name": seg.segment_name,
                    "segment_query": seg.segment_query,
                    "execution_details": seg.execution_details,
                    "dataset_name": seg.dataset_name,
                    "experiment_ready": seg.experiment_ready,
                    "segment_health": {
                        "row_count": seg.segment_health.row_count,
                        "data_distribution": seg.segment_health.data_distribution,
                        "target_distribution": seg.segment_health.target_distribution,
                        "temporal_distribution": seg.segment_health.temporal_distribution,
                        "entity_distribution": seg.segment_health.entity_distribution,
                        "health_score": seg.segment_health.health_score,
                        "health_assessment": seg.segment_health.health_assessment
                    },
                    "reasons": seg.reasons,
                    "recommendations": seg.recommendations
                }
                for seg in self.segments
            ]
        }
        if self.comparative_analysis:
            result["comparative_analysis"] = {
                "total_rows_across_segments": self.comparative_analysis.total_rows_across_segments,
                "best_health_score": self.comparative_analysis.best_health_score,
                "segment_with_best_health": self.comparative_analysis.segment_with_best_health,
                "recommended_segment_for_modeling": self.comparative_analysis.recommended_segment_for_modeling,
                "health_comparison": self.comparative_analysis.health_comparison
            }
        if self.experiment_configuration:
            result["experiment_configuration"] = self.experiment_configuration
        return result


@dataclass
class SegmentationRequest:
    """Request model for segmentation operations."""
    user_text: str  # Natural language segmentation request
    request: AgentInputsRequest  # Standard agent input request
    dataset_metadata: Dict[str, Any]  # Table metadata from fetch_column_name_datatype
    business_context: Optional[Dict[str, Any]] = None  # Additional business context
    target_column: Optional[str] = None  # Target column name if applicable

