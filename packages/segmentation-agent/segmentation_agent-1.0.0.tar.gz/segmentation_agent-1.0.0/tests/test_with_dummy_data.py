"""
Integration test with dummy data for the Segmentation Agent.

This test demonstrates the full workflow with mocked LLM responses.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine, text
import pandas as pd

from segmentation_agent import SegmentationAgent
from segmentation_agent.models import AgentInputsRequest


class TestSegmentationAgentWithDummyData:
    """Test the segmentation agent with dummy data."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        return SegmentationAgent()
    
    @pytest.fixture
    def dummy_data(self):
        """Create dummy customer data."""
        return pd.DataFrame({
            'customer_id': [f'CUST_{i:03d}' for i in range(1, 21)],
            'revenue': [15000, 12000, 8000, 6000, 4000, 3000, 2000, 15000, 11000, 7000,
                        5000, 3500, 2500, 18000, 13000, 9000, 5500, 4500, 3200, 2200],
            'age': [35, 42, 28, 55, 30, 25, 40, 38, 45, 32, 50, 27, 33, 48, 36, 29, 44, 31, 26, 39],
            'churn_target': [0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0],
            'region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West', 
                       'North', 'South', 'East', 'West', 'North', 'South', 'East', 'West',
                       'North', 'South', 'East', 'West'],
            'product_category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'A', 'B', 'C',
                                'A', 'B', 'C', 'A', 'B', 'A', 'C', 'B', 'A', 'C']
        })
    
    @pytest.fixture
    def db_engine(self, dummy_data):
        """Create in-memory SQLite database with dummy data."""
        # Use raw sqlite3 connection for pandas compatibility
        import sqlite3
        conn = sqlite3.connect(':memory:')
        dummy_data.to_sql('customer_data', conn, index=False, if_exists='replace')
        conn.close()
        
        # Create SQLAlchemy engine pointing to same in-memory database
        # Note: SQLite in-memory databases are per-connection, so we need to use a file-based approach
        import tempfile
        import os
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        # Populate using sqlite3
        conn = sqlite3.connect(temp_file.name)
        dummy_data.to_sql('customer_data', conn, index=False, if_exists='replace')
        conn.close()
        
        # Create SQLAlchemy engine
        engine = create_engine(f'sqlite:///{temp_file.name}')
        yield engine
        engine.dispose()
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def sample_request(self):
        """Sample AgentInputsRequest."""
        return AgentInputsRequest(
            conn=None,  # Will be set in tests
            auth_service_base_url="",
            project_name="test_project",
            schema="test_schema",
            table_name="customer_data",
            mappings={},
            use_case="churn_prediction",
            ml_approach="binary_classification",
            experiment_type="classification"
        )
    
    @pytest.fixture
    def dataset_metadata(self):
        """Sample dataset metadata."""
        return {
            "schema": "test_schema",
            "table_name": "customer_data",
            "columns": [
                {"column_name": "customer_id", "data_type": "VARCHAR"},
                {"column_name": "revenue", "data_type": "NUMBER"},
                {"column_name": "age", "data_type": "NUMBER"},
                {"column_name": "churn_target", "data_type": "BOOLEAN"},
                {"column_name": "region", "data_type": "VARCHAR"},
                {"column_name": "product_category", "data_type": "VARCHAR"}
            ],
            "column_count": 6
        }
    
    @patch('segmentation_agent.agent.SFNAIHandler')
    def test_full_workflow_phase1(self, mock_handler_class, agent, sample_request, dataset_metadata):
        """Test Phase 1: Understanding segmentation intent with dummy data."""
        # Mock LLM response for Phase 1
        mock_response_phase1 = {
            "segment_count": 3,
            "segments": [
                {
                    "segment_name": "high_value_customers",
                    "business_understanding": "Customers with revenue greater than 10000, representing the top tier of our customer base",
                    "identified_columns": ["customer_id", "revenue"],
                    "segmentation_logic": "Filter where revenue > 10000",
                    "confidence_score": 0.95
                },
                {
                    "segment_name": "medium_value_customers",
                    "business_understanding": "Customers with revenue between 5000 and 10000, representing the middle tier",
                    "identified_columns": ["customer_id", "revenue"],
                    "segmentation_logic": "Filter where revenue >= 5000 AND revenue <= 10000",
                    "confidence_score": 0.90
                },
                {
                    "segment_name": "low_value_customers",
                    "business_understanding": "Customers with revenue less than 5000, representing the lower tier",
                    "identified_columns": ["customer_id", "revenue"],
                    "segmentation_logic": "Filter where revenue < 5000",
                    "confidence_score": 0.90
                }
            ]
        }
        
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.route_to.return_value = json.dumps(mock_response_phase1)
        mock_handler_class.return_value = mock_handler
        agent.ai_handler = mock_handler
        
        # Test Phase 1
        user_text = "create 3 segments: high-value customers (revenue > 10000), medium-value (revenue 5000-10000), low-value (revenue < 5000)"
        
        result = agent.understand_segmentation_intent(
            user_text=user_text,
            request=sample_request,
            dataset_metadata=dataset_metadata
        )
        
        # Assertions
        assert result is not None
        assert result.status == "understanding_generated"
        assert result.segment_count == 3
        assert len(result.segments) == 3
        assert result.segments[0].segment_name == "high_value_customers"
        assert result.segments[1].segment_name == "medium_value_customers"
        assert result.segments[2].segment_name == "low_value_customers"
        assert all(seg.confidence_score > 0.8 for seg in result.segments)
        
        print("\n✅ Phase 1 Test Passed!")
        print(f"   Generated {result.segment_count} segments")
        for seg in result.segments:
            print(f"   - {seg.segment_name}: {seg.business_understanding[:50]}...")
    
    @patch('segmentation_agent.agent.SFNAIHandler')
    def test_full_workflow_phase2(self, mock_handler_class, agent, sample_request, dataset_metadata):
        """Test Phase 2: Generate SQL queries with dummy data."""
        # Mock LLM response for Phase 2
        mock_response_phase2 = {
            "segment_count": 3,
            "segments": [
                {
                    "segment_name": "high_value_customers",
                    "sql_query": "SELECT * FROM customer_data WHERE revenue > 10000",
                    "query_explanation": "Selects all customers with revenue greater than 10000",
                    "confidence_score": 0.95
                },
                {
                    "segment_name": "medium_value_customers",
                    "sql_query": "SELECT * FROM customer_data WHERE revenue >= 5000 AND revenue <= 10000",
                    "query_explanation": "Selects all customers with revenue between 5000 and 10000",
                    "confidence_score": 0.90
                },
                {
                    "segment_name": "low_value_customers",
                    "sql_query": "SELECT * FROM customer_data WHERE revenue < 5000",
                    "query_explanation": "Selects all customers with revenue less than 5000",
                    "confidence_score": 0.90
                }
            ]
        }
        
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.route_to.return_value = json.dumps(mock_response_phase2)
        mock_handler_class.return_value = mock_handler
        agent.ai_handler = mock_handler
        
        # Business understanding from Phase 1 (simulated)
        business_understandings = [
            {
                "segment_name": "high_value_customers",
                "business_understanding": "Customers with revenue > 10000",
                "identified_columns": ["customer_id", "revenue"],
                "segmentation_logic": "Filter where revenue > 10000"
            },
            {
                "segment_name": "medium_value_customers",
                "business_understanding": "Customers with revenue between 5000 and 10000",
                "identified_columns": ["customer_id", "revenue"],
                "segmentation_logic": "Filter where revenue >= 5000 AND revenue <= 10000"
            },
            {
                "segment_name": "low_value_customers",
                "business_understanding": "Customers with revenue < 5000",
                "identified_columns": ["customer_id", "revenue"],
                "segmentation_logic": "Filter where revenue < 5000"
            }
        ]
        
        # Test Phase 2
        result = agent.generate_segmentation_query(
            business_understandings=business_understandings,
            request=sample_request,
            dataset_metadata=dataset_metadata
        )
        
        # Assertions
        assert result is not None
        assert result.status == "queries_generated"
        assert result.segment_count == 3
        assert len(result.segments) == 3
        
        for seg in result.segments:
            assert "SELECT" in seg.sql_query
            assert "WHERE" in seg.sql_query
            assert seg.dry_run_status in ["valid", "invalid"]
        
        print("\n✅ Phase 2 Test Passed!")
        print(f"   Generated {result.segment_count} SQL queries")
        for seg in result.segments:
            print(f"   - {seg.segment_name}: {seg.sql_query}")
    
    def test_full_workflow_phase3(self, agent, dataset_metadata):
        """Test Phase 3: Generate health analysis (no SQL execution)."""
        # Test queries (from Phase 2)
        segment_queries = [
            {
                "segment_name": "high_value_customers",
                "sql_query": "SELECT * FROM customer_data WHERE revenue > 10000"
            },
            {
                "segment_name": "medium_value_customers",
                "sql_query": "SELECT * FROM customer_data WHERE revenue >= 5000 AND revenue <= 10000"
            },
            {
                "segment_name": "low_value_customers",
                "sql_query": "SELECT * FROM customer_data WHERE revenue < 5000"
            }
        ]
        
        # Optional: Provide pre-computed stats (simulating data from other services)
        segment_data_stats = [
            {"row_count": 6},
            {"row_count": 6},
            {"row_count": 8}
        ]
        
        # Mock LLM response for health analysis
        mock_health_response = {
            "data_distribution": {
                "revenue_mean": 7500,
                "revenue_std": 4500
            },
            "health_score": 0.75,
            "health_assessment": "good",
            "reasons": ["Segment has sufficient data points", "Revenue distribution is balanced"],
            "recommendations": ["Consider additional features", "Monitor segment performance"]
        }
        
        with patch.object(agent.ai_handler, 'route_to', return_value=json.dumps(mock_health_response)):
            # Test Phase 3 (no SQL execution - generates analysis only)
            result = agent.analyze_multiple_segment_health(
                segment_queries=segment_queries,
                dataset_metadata=dataset_metadata,
                target_column="churn_target",
                segment_data_stats=segment_data_stats
            )
            
            # Assertions
            assert result is not None
            assert result.status == "success"
            assert result.segment_count == 3
            assert len(result.segments) == 3
            
            # Check that each segment has health analysis
            for seg in result.segments:
                assert seg.segment_name in ["high_value_customers", "medium_value_customers", "low_value_customers"]
                assert seg.experiment_ready in [True, False]
                assert "analysis_generated" in seg.execution_details.get("status", "")
            
            # Check comparative analysis
            if result.comparative_analysis:
                assert result.comparative_analysis.total_rows_across_segments > 0
                assert result.comparative_analysis.best_health_score >= 0
            
            print("\n✅ Phase 3 Test Passed!")
            print(f"   Generated health analysis for {result.segment_count} segments")
            for seg in result.segments:
                print(f"   - {seg.segment_name}: health={seg.segment_health.health_score:.2f}, "
                      f"assessment={seg.segment_health.health_assessment}")
    
    @patch('segmentation_agent.agent.SFNAIHandler')
    def test_end_to_end_workflow(self, mock_handler_class, agent, db_engine, sample_request, dataset_metadata):
        """Test complete end-to-end workflow with dummy data."""
        print("\n" + "="*60)
        print("Testing End-to-End Segmentation Workflow")
        print("="*60)
        
        # Mock responses for all phases
        mock_phase1_response = {
            "segment_count": 2,
            "segments": [
                {
                    "segment_name": "high_revenue",
                    "business_understanding": "High revenue customers",
                    "identified_columns": ["revenue"],
                    "segmentation_logic": "revenue > 10000",
                    "confidence_score": 0.9
                },
                {
                    "segment_name": "low_revenue",
                    "business_understanding": "Low revenue customers",
                    "identified_columns": ["revenue"],
                    "segmentation_logic": "revenue <= 10000",
                    "confidence_score": 0.9
                }
            ]
        }
        
        mock_phase2_response = {
            "segment_count": 2,
            "segments": [
                {
                    "segment_name": "high_revenue",
                    "sql_query": "SELECT * FROM customer_data WHERE revenue > 10000",
                    "query_explanation": "High revenue segment",
                    "confidence_score": 0.9
                },
                {
                    "segment_name": "low_revenue",
                    "sql_query": "SELECT * FROM customer_data WHERE revenue <= 10000",
                    "query_explanation": "Low revenue segment",
                    "confidence_score": 0.9
                }
            ]
        }
        
        mock_health_response = {
            "health_score": 0.8,
            "health_assessment": "good",
            "reasons": ["Good data distribution"],
            "recommendations": ["Continue monitoring"]
        }
        
        # Setup mock to return different responses based on call
        mock_handler = MagicMock()
        call_count = [0]
        
        def mock_route_to(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return json.dumps(mock_phase1_response)
            elif call_count[0] == 2:
                return json.dumps(mock_phase2_response)
            else:
                return json.dumps(mock_health_response)
        
        mock_handler.route_to.side_effect = mock_route_to
        mock_handler_class.return_value = mock_handler
        agent.ai_handler = mock_handler
        
        # Phase 1: Understand intent
        print("\n📋 Phase 1: Understanding Segmentation Intent...")
        user_text = "create 2 segments: high revenue (revenue > 10000) and low revenue (revenue <= 10000)"
        understanding = agent.understand_segmentation_intent(
            user_text=user_text,
            request=sample_request,
            dataset_metadata=dataset_metadata
        )
        assert understanding.segment_count == 2
        print(f"   ✓ Generated understanding for {understanding.segment_count} segments")
        
        # Phase 2: Generate SQL queries
        print("\n🔧 Phase 2: Generating SQL Queries...")
        business_understandings = [
            {
                "segment_name": seg.segment_name,
                "business_understanding": seg.business_understanding,
                "identified_columns": seg.identified_columns,
                "segmentation_logic": seg.segmentation_logic
            }
            for seg in understanding.segments
        ]
        
        queries = agent.generate_segmentation_query(
            business_understandings=business_understandings,
            request=sample_request,
            dataset_metadata=dataset_metadata
        )
        assert queries.segment_count == 2
        print(f"   ✓ Generated {queries.segment_count} SQL queries")
        
        # Phase 3: Generate health analysis
        print("\n📊 Phase 3: Generating Segment Health Analysis...")
        segment_queries = [
            {"segment_name": seg.segment_name, "sql_query": seg.sql_query}
            for seg in queries.segments
        ]
        
        # Optional: Provide pre-computed stats (simulating data from other services)
        segment_data_stats = [
            {"row_count": 6},  # high_revenue
            {"row_count": 14}  # low_revenue
        ]
        
        # Reset call count for health analysis
        call_count[0] = 0
        
        health = agent.analyze_multiple_segment_health(
            segment_queries=segment_queries,
            dataset_metadata=dataset_metadata,
            target_column="churn_target",
            segment_data_stats=segment_data_stats
        )
        assert health.segment_count == 2
        print(f"   ✓ Analyzed {health.segment_count} segments")
        
        # Print summary
        print("\n" + "="*60)
        print("✅ End-to-End Test Completed Successfully!")
        print("="*60)
        print(f"\nSummary:")
        print(f"  - Segments Created: {health.segment_count}")
        print(f"  - Total Rows: {health.comparative_analysis.total_rows_across_segments if health.comparative_analysis else 'N/A'}")
        for seg in health.segments:
            print(f"  - {seg.segment_name}: health={seg.segment_health.health_score:.2f}, "
                  f"assessment={seg.segment_health.health_assessment}")

