"""
Segmentation Agent - Intelligent dataset segmentation for ML workflows.

This agent provides three-phase segmentation:
1. Understanding & Validation: Parse user intent and generate business understanding
2. SQL Generation: Generate executable SQL queries from validated understanding
3. Health Analysis: Analyze segment data and generate health metrics
"""

import json
import logging
import os
import sys
import traceback
from typing import Any, Dict, List, Optional, Tuple

from sfn_blueprint import SFNAIHandler

from .config import SegmentationConfig
from .constants import (
    SYSTEM_PROMPT_HEALTH_ANALYSIS,
    SYSTEM_PROMPT_INTENT_UNDERSTANDING,
    SYSTEM_PROMPT_SQL_GENERATION,
    format_health_analysis_prompt,
    format_intent_understanding_prompt,
    format_sql_generation_prompt,
)
from .models import (
    AgentInputsRequest,
    ComparativeAnalysis,
    SegmentationHealth,
    SegmentationQuery,
    SegmentationUnderstanding,
    SegmentHealth,
    SegmentHealthMetrics,
    SegmentQuery,
    SegmentUnderstanding,
)
from .utils import (
    format_segment_name,
    get_final_table_name,
    validate_sql_syntax,
)


class SegmentationAgent:
    """
    Main agent class for dataset segmentation.

    Provides three independent phases:
    1. understand_segmentation_intent: Parse user text and generate business understanding
    2. generate_segmentation_query: Generate SQL queries from validated understanding
    3. analyze_segment_health: Analyze segment data and generate health metrics
    """

    def __init__(self, config: Optional[SegmentationConfig] = None):
        """
        Initialize the agent with configuration.

        Args:
            config: Optional SegmentationConfig instance. If not provided, a default will be used.
        """
        # Initialize configuration
        self.config = config or SegmentationConfig()

        # Set OPENAI_API_KEY environment variable if LLM_API_KEY is set and provider is openai
        # This is needed because sfn_blueprint reads from OPENAI_API_KEY
        if self.config.ai_provider == "openai" and self.config.api_key:
            os.environ["OPENAI_API_KEY"] = self.config.api_key

        # Setup logging (matching target_questions_generator_agent pattern)
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Initialize AI handler (centralized LLM handler)
        self.ai_handler = SFNAIHandler()

        self.logger.info("SegmentationAgent initialized")

    # =============================================================================
    # PHASE 1: Understanding & Validation
    # =============================================================================

    def understand_segmentation_intent(
        self,
        user_text: str,
        request: AgentInputsRequest,
        dataset_metadata: Dict[str, Any],
        business_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[SegmentationUnderstanding, Dict[str, Any]]:
        """
        Phase 1: Understand user intent and generate business understanding.

        This method:
        - Parses natural language segmentation request
        - Identifies single or multiple segments
        - Generates business-level understanding for each segment
        - Returns understanding for user validation

        Args:
            user_text: Natural language segmentation request
            request: Agent input request with connection and metadata
            dataset_metadata: Table metadata with columns and data types
            business_context: Optional additional business context

        Returns:
            SegmentationUnderstanding with business understanding for each segment
        """
        try:
            self.logger.info(
                f"Phase 1: Understanding segmentation intent for: {user_text[:100]}..."
            )

            # Prepare business context
            if business_context is None:
                business_context = {
                    "domain": request.get("project_name", "general"),
                    "description": f"Use case: {request.get('use_case', 'N/A')}",
                }

            # Format prompts (include mappings for column name conversion)
            system_prompt = SYSTEM_PROMPT_INTENT_UNDERSTANDING
            user_prompt = format_intent_understanding_prompt(
                user_text=user_text,
                dataset_metadata=dataset_metadata,
                business_context=business_context,
                use_case=request.get("use_case", ""),
                ml_approach=request.get("ml_approach", ""),
                mappings=request.get("mappings", {}),
            )

            # Call LLM
            response, token_summary = self.ai_handler.route_to(
                llm_provider=self.config.ai_provider,
                configuration={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "model": self.config.model_name,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "api_key": self.config.api_key,
                },
                model=self.config.model_name,
            )

            # Parse response
            if isinstance(response, list):
                response = response[0] if response else ""
            if isinstance(response, str):
                # Try to extract JSON from response
                response = response.replace("```json", "").replace("```", "").strip()
                response = json.loads(response)

            # Build result
            segment_count = response.get("segment_count", 1)
            segments_data = response.get("segments", [])

            segments = []
            for seg_data in segments_data:
                segments.append(
                    SegmentUnderstanding(
                        segment_name=format_segment_name(
                            seg_data.get("segment_name", "segment_1")
                        ),
                        business_understanding=seg_data.get(
                            "business_understanding", ""
                        ),
                        identified_columns=seg_data.get("identified_columns", []),
                        segmentation_logic=seg_data.get("segmentation_logic", ""),
                        confidence_score=seg_data.get("confidence_score", 0.0),
                    )
                )

            result = SegmentationUnderstanding(
                status="understanding_generated",
                segment_count=segment_count,
                segments=segments,
                requires_confirmation=True,
            )

            self.logger.info(
                f"Phase 1 complete: Generated understanding for {segment_count} segment(s)"
            )

            return result, token_summary
        except Exception as e:
            self.logger.error(
                f"Error in understand_segmentation_intent: {str(e)}\n{traceback.format_exc()}"
            )
            return SegmentationUnderstanding(
                status="error",
                segment_count=0,
                segments=[],
                requires_confirmation=False,
            ), {}

    # =============================================================================
    # PHASE 2: SQL Generation & Validation
    # =============================================================================

    def generate_segmentation_query(
        self,
        business_understandings: List[Dict[str, Any]],
        request: AgentInputsRequest,
        dataset_metadata: Dict[str, Any],
    ) -> Tuple[SegmentationQuery, Dict[str, Any]]:
        """
        Phase 2: Generate SQL queries from validated business understanding.

        This method:
        - Takes confirmed business understanding (from Phase 1, possibly modified by user)
        - Generates executable SQL queries for each segment
        - Validates SQL syntax
        - Returns queries ready for execution

        Args:
            business_understandings: List of business understanding dictionaries (from Phase 1)
            request: Agent input request with connection and metadata
            dataset_metadata: Table metadata with columns and data types

        Returns:
            SegmentationQuery with SQL queries for each segment
        """
        try:
            self.logger.info(
                f"Phase 2: Generating SQL queries for {len(business_understandings)} segment(s)"
            )

            # Get source table information
            experiment_type = request.get("experiment_type", "classification")
            project_name = request.get("project_name", "")

            source_table, source_schema = get_final_table_name(
                experiment_type, project_name
            )

            # Use schema from request if provided, otherwise use computed schema
            source_schema = request.get("schema") or source_schema
            # Format prompts
            system_prompt = SYSTEM_PROMPT_SQL_GENERATION

            user_prompt = format_sql_generation_prompt(
                business_understandings=business_understandings,
                dataset_metadata=dataset_metadata,
                source_schema=source_schema,
                source_table=source_table,
            )

            # Call LLM
            response, token_summary = self.ai_handler.route_to(
                llm_provider=self.config.ai_provider,
                configuration={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "model": self.config.model_name,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "api_key": self.config.api_key,
                },
                model=self.config.model_name,
            )

            # Parse response
            if isinstance(response, list):
                response = response[0] if response else ""
            if isinstance(response, str):
                response = response.replace("```json", "").replace("```", "").strip()
                response = json.loads(response)

            # Build result
            segment_count = response.get("segment_count", len(business_understandings))
            segments_data = response.get("segments", [])

            segments = []
            total_estimated_rows = 0

            for seg_data in segments_data:
                sql_query = seg_data.get("sql_query", "")

                # Validate SQL syntax
                is_valid, error_msg = validate_sql_syntax(sql_query)
                dry_run_status = "valid" if is_valid else f"invalid: {error_msg}"

                segment_query = SegmentQuery(
                    segment_name=format_segment_name(
                        seg_data.get("segment_name", "segment_1")
                    ),
                    sql_query=sql_query,
                    query_explanation=seg_data.get("query_explanation", ""),
                    dry_run_status=dry_run_status,
                    estimated_row_count=seg_data.get("estimated_row_count"),
                    confidence_score=seg_data.get("confidence_score", 0.0),
                )

                segments.append(segment_query)

                if segment_query.estimated_row_count:
                    total_estimated_rows += segment_query.estimated_row_count

            result = SegmentationQuery(
                status="queries_generated",
                segment_count=segment_count,
                segments=segments,
                total_estimated_rows=total_estimated_rows
                if total_estimated_rows > 0
                else None,
            )

            self.logger.info(
                f"Phase 2 complete: Generated {segment_count} SQL query/queries"
            )

            return result, token_summary
        except Exception as e:
            self.logger.error(
                f"Error in generate_segmentation_query: {str(e)}\n{traceback.format_exc()}"
            )

            return SegmentationQuery(status="error", segment_count=0, segments=[]), {}

    # =============================================================================
    # PHASE 3: Health Analysis
    # =============================================================================

    def analyze_segment_health(
        self,
        segment_query: str,
        segment_name: str,
        dataset_metadata: Dict[str, Any],
        target_column: Optional[str] = None,
        segment_data_stats: Optional[Dict[str, Any]] = None,
    ) -> Tuple[SegmentHealth, Dict[str, Any]]:
        """
        Generate health analysis for a single segment.

        Note: This method generates health analysis logic/queries only.
        Actual SQL execution and data retrieval should be handled by other services.

        Args:
            segment_query: SQL query for the segment
            segment_name: Name of the segment
            dataset_metadata: Table metadata
            target_column: Optional target column name
            segment_data_stats: Optional pre-computed statistics (if available from other services)

        Returns:
            SegmentHealth with health analysis logic and recommendations
        """
        try:
            self.logger.info(
                f"Phase 3: Generating health analysis for segment: {segment_name}"
            )

            # Call LLM for health analysis generation
            system_prompt = SYSTEM_PROMPT_HEALTH_ANALYSIS

            user_prompt = format_health_analysis_prompt(
                segment_name=segment_name,
                segment_query=segment_query,
                dataset_metadata=dataset_metadata,
                target_column=target_column,
            )

            health_response, token_summary = self.ai_handler.route_to(
                llm_provider=self.config.ai_provider,
                configuration={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "model": self.config.model_name,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "api_key": self.config.api_key,
                },
                model=self.config.model_name,
            )

            # Parse health analysis response
            health_data = {}
            reasons = []
            recommendations = []
            health_score = 0.5  # Default
            health_assessment = "unknown"

            if isinstance(health_response, str):
                try:
                    health_data = json.loads(
                        health_response.replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )
                    reasons = health_data.get("reasons", [])
                    recommendations = health_data.get("recommendations", [])
                    if "health_score" in health_data:
                        health_score = health_data["health_score"]
                    if "health_assessment" in health_data:
                        health_assessment = health_data["health_assessment"]
                except Exception:
                    reasons = [health_response]

            # Use provided stats if available, otherwise use defaults
            row_count = (
                segment_data_stats.get("row_count", 0) if segment_data_stats else 0
            )

            return SegmentHealth(
                segment_name=segment_name,
                segment_query=segment_query,
                execution_details={
                    "status": "analysis_generated",
                    "note": "SQL execution and data retrieval handled by other services",
                },
                dataset_name=f"{segment_name}_dataset",
                experiment_ready=True,
                segment_health=SegmentHealthMetrics(
                    row_count=row_count,
                    data_distribution=health_data.get("data_distribution", {}),
                    target_distribution=health_data.get("target_distribution"),
                    temporal_distribution=health_data.get("temporal_distribution"),
                    entity_distribution=health_data.get("entity_distribution"),
                    health_score=health_score,
                    health_assessment=health_assessment,
                ),
                reasons=reasons
                if reasons
                else ["Health analysis generated based on query structure"],
                recommendations=recommendations,
            ), token_summary
        except Exception as e:
            self.logger.error(
                f"Error in analyze_segment_health: {str(e)}\n{traceback.format_exc()}"
            )

            return SegmentHealth(
                segment_name=segment_name,
                segment_query=segment_query,
                execution_details={"status": "error", "error": str(e)},
                dataset_name=f"{segment_name}_dataset",
                experiment_ready=False,
                segment_health=SegmentHealthMetrics(
                    row_count=0, health_score=0.0, health_assessment="poor"
                ),
                reasons=[f"Error generating health analysis: {str(e)}"],
                recommendations=["Review query and try again"],
            ), {}

    def analyze_multiple_segment_health(
        self,
        segment_queries: List[Dict[str, Any]],
        dataset_metadata: Dict[str, Any],
        target_column: Optional[str] = None,
        segment_data_stats: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[SegmentationHealth, Dict[str, Any]]:
        """
        Analyze health metrics for multiple segments and provide comparative analysis.

        Args:
            segment_queries: List of segment query dictionaries with 'segment_name' and 'sql_query'
            dataset_metadata: Table metadata
            target_column: Optional target column name
            segment_data_stats: Optional list of pre-computed statistics for each segment

        Returns:
            SegmentationHealth with health analysis for all segments and comparative analysis

        Note: This method generates health analysis logic only.
        Actual SQL execution and data retrieval should be handled by other services.
        """
        try:
            self.logger.info(
                f"Phase 3: Generating health analysis for {len(segment_queries)} segment(s)"
            )

            segments = []
            total_rows = 0
            health_scores = {}

            final_token_summary = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
            }

            # Generate health analysis for each segment
            for i, seg_query in enumerate(segment_queries):
                seg_stats = (
                    segment_data_stats[i]
                    if segment_data_stats and i < len(segment_data_stats)
                    else None
                )

                segment_health, token_summary = self.analyze_segment_health(
                    segment_query=seg_query.get("sql_query", ""),
                    segment_name=seg_query.get("segment_name", "unknown"),
                    dataset_metadata=dataset_metadata,
                    target_column=target_column,
                    segment_data_stats=seg_stats,
                )

                final_token_summary["prompt_tokens"] += token_summary["prompt_tokens"]
                final_token_summary["completion_tokens"] += token_summary["completion_tokens"]
                final_token_summary["total_tokens"] += token_summary["total_tokens"]
                final_token_summary["total_cost_usd"] += token_summary["total_cost_usd"]

                segments.append(segment_health)
                total_rows += segment_health.segment_health.row_count

                health_scores[segment_health.segment_name] = (
                    segment_health.segment_health.health_score
                )

            # Generate comparative analysis
            if len(segments) > 1:
                best_health_score = max(health_scores.values())
                best_segment = max(health_scores.items(), key=lambda x: x[1])[0]

                comparative_analysis = ComparativeAnalysis(
                    total_rows_across_segments=total_rows,
                    best_health_score=best_health_score,
                    segment_with_best_health=best_segment,
                    recommended_segment_for_modeling=best_segment,
                    health_comparison=health_scores,
                )

                experiment_config = {
                    "can_run_parallel_experiments": True,
                    "recommended_experiment_order": sorted(
                        health_scores.items(), key=lambda x: x[1], reverse=True
                    ),
                }
            else:
                comparative_analysis = None
                experiment_config = None

            result = SegmentationHealth(
                status="success",
                segment_count=len(segments),
                total_segments_processed=len(segments),
                segments=segments,
                comparative_analysis=comparative_analysis,
                experiment_configuration=experiment_config,
            )

            self.logger.info(f"Phase 3 complete: Analyzed {len(segments)} segment(s)")
            return result, final_token_summary
        except Exception as e:
            self.logger.error(
                f"Error in analyze_multiple_segment_health: {str(e)}\n{traceback.format_exc()}"
            )

            return SegmentationHealth(
                status="error", segment_count=0, total_segments_processed=0, segments=[]
            ), {}

    # =============================================================================
    # Convenience Methods
    # =============================================================================

    def __call__(
        self,
        user_text: str,
        request: AgentInputsRequest,
        dataset_metadata: Dict[str, Any],
        business_context: Optional[Dict[str, Any]] = None,
    ) -> SegmentationUnderstanding:
        """
        Convenience method to call Phase 1 directly.

        Args:
            user_text: Natural language segmentation request
            request: Agent input request
            dataset_metadata: Table metadata
            business_context: Optional business context

        Returns:
            SegmentationUnderstanding
        """
        return self.understand_segmentation_intent(
            user_text=user_text,
            request=request,
            dataset_metadata=dataset_metadata,
            business_context=business_context,
        )
