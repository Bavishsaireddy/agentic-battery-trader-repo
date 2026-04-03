import json
from unittest.mock import patch, MagicMock
import pytest

from agent.planner import Planner
from agent.analyzer import Analyzer
from agent.reporter import Reporter
from core.registry import ToolRegistry
from core.evidence import EvidenceStore

@pytest.fixture
def mock_tool_registry():
    registry = ToolRegistry()
    @registry.register
    def dummy_tool(df):
        pass
    return registry

@pytest.fixture
def mock_evidence_store():
    store = EvidenceStore()
    store.set("dummy_key", {"dummy": "value"})
    return store

@patch("agent.planner.LLM_PROVIDER", "openai")
@patch("agent.planner.OpenAI")
def test_planner_parsing_success(mock_openai_class, mock_tool_registry):
    # Setup mock OpenAI client
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_response = MagicMock()
    # Provide a valid JSON string wrapped in markdown block
    mock_response.choices[0].message.content = '```json\n[{"tool": "dummy_tool", "args": {}}]\n```'
    mock_client.chat.completions.create.return_value = mock_response

    planner = Planner(mock_tool_registry)
    plan = planner.generate_plan()

    assert isinstance(plan, list)
    assert len(plan) == 1
    assert plan[0]["tool"] == "dummy_tool"
    mock_client.chat.completions.create.assert_called_once()

@patch("agent.planner.LLM_PROVIDER", "openai")
@patch("agent.planner.OpenAI")
def test_planner_parsing_failure(mock_openai_class, mock_tool_registry):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_response = MagicMock()
    # Provide an invalid JSON string to trigger parsing error
    mock_response.choices[0].message.content = 'Hello this is not json'
    mock_client.chat.completions.create.return_value = mock_response

    planner = Planner(mock_tool_registry)
    with pytest.raises(ValueError, match="Failed to parse LLM plan"):
        planner.generate_plan()

@patch("agent.analyzer.LLM_PROVIDER", "openai")
@patch("agent.analyzer.OpenAI")
def test_analyzer_parsing_success(mock_openai_class, mock_evidence_store):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_response = MagicMock()
    # Provide a valid JSON output
    mock_response.choices[0].message.content = '```json\n{"gap_found": true, "details": "Issue detected"}\n```'
    mock_client.chat.completions.create.return_value = mock_response

    analyzer = Analyzer(mock_evidence_store)
    analysis = analyzer.analyze()

    assert isinstance(analysis, dict)
    assert analysis["gap_found"] is True
    assert analysis["details"] == "Issue detected"
    mock_client.chat.completions.create.assert_called_once()

@patch("agent.reporter.LLM_PROVIDER", "openai")
@patch("agent.reporter.OpenAI")
def test_reporter_generation(mock_openai_class):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '# Trader Report\n## Summary\nEverything is good.'
    mock_client.chat.completions.create.return_value = mock_response

    analyzer_output = {"gap_found": False}
    reporter = Reporter(analyzer_output)
    report_md = reporter.generate_report()

    assert "Trader Report" in report_md
    mock_client.chat.completions.create.assert_called_once()
