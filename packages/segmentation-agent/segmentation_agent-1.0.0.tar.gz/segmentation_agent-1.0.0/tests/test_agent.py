"""
Tests for the Segmentation Agent.
"""
import pytest
import json
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from segmentation_agent import SegmentationAgent
from segmentation_agent.models import (
    AgentInputsRequest,
    SegmentationUnderstanding,
    SegmentationQuery,
    SegmentationHealth
)


class TestSegmentationAgent:
    """Test cases for the Segmentation Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        return SegmentationAgent()
    
    @pytest.fixture
    def sample_request(self):
        """Sample AgentInputsRequest for testing."""
        return AgentInputsRequest(
            conn=None,
            auth_service_base_url="",
            project_name="test_project",
            schema="test_schema",
            table_name="classification_experiment_final_dataset",
            mappings={},
            use_case="churn_prediction",
            ml_approach="binary_classification",
            experiment_type="classification"
        )
    
    @pytest.fixture
    def sample_dataset_metadata(self):
        """Sample dataset metadata."""
        return {
            "schema": "test_schema",
            "table_name": "classification_experiment_final_dataset",
            "columns": [
                {"column_name": "customer_id", "data_type": "VARCHAR"},
                {"column_name": "revenue", "data_type": "NUMBER"},
                {"column_name": "churn_target", "data_type": "BOOLEAN"}
            ],
            "column_count": 3
        }
    
    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly."""
        assert agent is not None
        assert agent.ai_handler is not None
        assert agent.config is not None
        assert agent.logger is not None
    
    @patch('segmentation_agent.agent.SFNAIHandler')
    def test_understand_segmentation_intent_single_segment(self, mock_handler_class, agent, sample_request, sample_dataset_metadata):
        """Test Phase 1: Understanding single segment intent with mocked LLM response."""
        # Mock LLM response
        mock_response = {
            "segment_count": 1,
            "segments": [
                {
                    "segment_name": "high_value_customers",
                    "business_understanding": "Segment for customers with revenue > 10000",
                    "identified_columns": ["customer_id", "revenue"],
                    "segmentation_logic": "Filter where revenue > 10000",
                    "confidence_score": 0.90
                }
            ]
        }
        
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.route_to.return_value = json.dumps(mock_response)
        mock_handler_class.return_value = mock_handler
        agent.ai_handler = mock_handler
        
        # Call method
        user_text = "create segment for high-value customers with revenue > 10000"
        result = agent.understand_segmentation_intent(
            user_text=user_text,
            request=sample_request,
            dataset_metadata=sample_dataset_metadata
        )
        
        # Assertions
        assert result is not None
        assert result.status == "understanding_generated"
        assert result.segment_count == 1
        assert len(result.segments) == 1
        assert result.segments[0].segment_name == "high_value_customers"
        assert result.requires_confirmation is True
    
    @patch('segmentation_agent.agent.SFNAIHandler')
    def test_understand_segmentation_intent_multiple_segments(self, mock_handler_class, agent, sample_request, sample_dataset_metadata):
        """Test Phase 1: Understanding multiple segments intent."""
        # Mock LLM response
        mock_response = {
            "segment_count": 3,
            "segments": [
                {
                    "segment_name": "high_value_customers",
                    "business_understanding": "Segment for customers with revenue > 10000",
                    "identified_columns": ["customer_id", "revenue"],
                    "segmentation_logic": "Filter where revenue > 10000",
                    "confidence_score": 0.90
                },
                {
                    "segment_name": "medium_value_customers",
                    "business_understanding": "Segment for customers with revenue between 5000 and 10000",
                    "identified_columns": ["customer_id", "revenue"],
                    "segmentation_logic": "Filter where revenue >= 5000 AND revenue <= 10000",
                    "confidence_score": 0.90
                },
                {
                    "segment_name": "low_value_customers",
                    "business_understanding": "Segment for customers with revenue < 5000",
                    "identified_columns": ["customer_id", "revenue"],
                    "segmentation_logic": "Filter where revenue < 5000",
                    "confidence_score": 0.90
                }
            ]
        }
        
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.route_to.return_value = json.dumps(mock_response)
        mock_handler_class.return_value = mock_handler
        agent.ai_handler = mock_handler
        
        # Call method
        user_text = "create 3 segments: high-value customers (revenue > 10000), medium-value (revenue 5000-10000), low-value (revenue < 5000)"
        result = agent.understand_segmentation_intent(
            user_text=user_text,
            request=sample_request,
            dataset_metadata=sample_dataset_metadata
        )
        
        # Assertions
        assert result is not None
        assert result.status == "understanding_generated"
        assert result.segment_count == 3
        assert len(result.segments) == 3
        assert all(seg.confidence_score > 0 for seg in result.segments)
    
    @patch('segmentation_agent.agent.SFNAIHandler')
    def test_generate_segmentation_query(self, mock_handler_class, agent, sample_request, sample_dataset_metadata):
        """Test Phase 2: Generate SQL queries from business understanding."""
        # Mock LLM response
        mock_response = {
            "segment_count": 1,
            "segments": [
                {
                    "segment_name": "high_value_customers",
                    "sql_query": "SELECT * FROM test_schema.classification_experiment_final_dataset WHERE revenue > 10000",
                    "query_explanation": "This query segments data by high revenue customers",
                    "confidence_score": 0.90
                }
            ]
        }
        
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.route_to.return_value = json.dumps(mock_response)
        mock_handler_class.return_value = mock_handler
        agent.ai_handler = mock_handler
        
        # Business understanding (from Phase 1)
        business_understandings = [
            {
                "segment_name": "high_value_customers",
                "business_understanding": "Segment for customers with revenue > 10000",
                "identified_columns": ["customer_id", "revenue"],
                "segmentation_logic": "Filter where revenue > 10000"
            }
        ]
        
        # Call method
        result = agent.generate_segmentation_query(
            business_understandings=business_understandings,
            request=sample_request,
            dataset_metadata=sample_dataset_metadata
        )
        
        # Assertions
        assert result is not None
        assert result.status == "queries_generated"
        assert result.segment_count == 1
        assert len(result.segments) == 1
        assert "SELECT" in result.segments[0].sql_query
        assert "WHERE" in result.segments[0].sql_query
        assert result.segments[0].dry_run_status in ["valid", "invalid"]
    
    def test_validate_sql_syntax(self):
        """Test SQL syntax validation."""
        from segmentation_agent.utils import validate_sql_syntax
        
        # Valid query
        valid_query = "SELECT * FROM schema.table WHERE revenue > 10000"
        is_valid, error = validate_sql_syntax(valid_query)
        assert is_valid is True
        assert error is None
        
        # Invalid query - no SELECT
        invalid_query = "FROM schema.table WHERE revenue > 10000"
        is_valid, error = validate_sql_syntax(invalid_query)
        assert is_valid is False
        assert error is not None
        
        # Invalid query - contains DROP (will fail SELECT check first)
        dangerous_query = "DROP TABLE schema.table"
        is_valid, error = validate_sql_syntax(dangerous_query)
        assert is_valid is False
        assert error is not None
        # DROP query fails SELECT check, not keyword check
        assert "SELECT" in error or "DROP" in error
    
    def test_format_segment_name(self):
        """Test segment name formatting."""
        from segmentation_agent.utils import format_segment_name
        
        # Test basic formatting
        assert format_segment_name("High Value Customers") == "high_value_customers"
        assert format_segment_name("Segment 1") == "segment_1"
        
        # Test with special characters
        assert format_segment_name("Segment-1") == "segment1"
        assert format_segment_name("Segment@1") == "segment1"
        
        # Test starting with number
        assert format_segment_name("1st Segment") == "segment_1st_segment"
    
    def test_get_final_table_name(self):
        """Test final table name generation."""
        from segmentation_agent.utils import get_final_table_name
        
        table_name, schema = get_final_table_name("classification", "my_project")
        assert table_name == "classification_experiment_final_dataset"
        assert schema == "my_project_operations"
    
    @pytest.mark.skip(reason="Requires actual database connection")
    def test_dry_run_query(self, agent, db_engine):
        """Test dry run query validation."""
        # This test requires actual database connection
        # Skipped by default, can be enabled for integration testing
        query = "SELECT * FROM customer_data WHERE revenue > 10000 LIMIT 0"
        result = agent.dry_run_query(
            conn=db_engine.connect(),
            query=query,
            schema_name="main"
        )
        assert result is not None
        assert "status" in result
    
    @patch('segmentation_agent.agent.SFNAIHandler')
    def test_analyze_segment_health(self, mock_handler_class, agent, sample_dataset_metadata):
        """Test Phase 3: Generate health analysis (no SQL execution)."""
        # Mock LLM response for health analysis
        mock_health_response = {
            "health_score": 0.75,
            "health_assessment": "good",
            "reasons": ["Segment has good data distribution"],
            "recommendations": ["Continue monitoring"]
        }
        
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.route_to.return_value = json.dumps(mock_health_response)
        mock_handler_class.return_value = mock_handler
        agent.ai_handler = mock_handler
        
        query = "SELECT * FROM customer_data WHERE revenue > 10000"
        result = agent.analyze_segment_health(
            segment_query=query,
            segment_name="high_value_customers",
            dataset_metadata=sample_dataset_metadata,
            target_column="churn_target",
            segment_data_stats={"row_count": 100}
        )
        assert result is not None
        assert result.segment_name == "high_value_customers"
        assert result.experiment_ready in [True, False]
        assert "analysis_generated" in result.execution_details.get("status", "")

