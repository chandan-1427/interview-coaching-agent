"""Test suite for the AI Interview Coach main agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Note: Adjust the import path if your file is named differently
from ai_interview_coach.main import (
    InterviewState,
    analyzer_node,
    narrative_node,
    alternative_node,
    polish_node,
    run_agent,
    handler,
)


@pytest.fixture
def mock_interview_state() -> InterviewState:
    """Provides a standard state dictionary for node testing."""
    return {
        "question": "How do you handle dependency conflicts?",
        "user_memory": "User previously struggled with system design.",
        "exa_research": "Real-world inspiration: React State Mgt",
        "intent_summary": "{\"hidden_fear\": \"scale\"}",
        "narrative_script": "I used tools to fix the issue.",
        "alternatives": "We considered X, but rejected it.",
        "final_response": "This is the final script."
    }


# --- NODE TESTS ---

@pytest.mark.asyncio
async def test_analyzer_node(mock_interview_state):
    """Test that analyzer_node formats prompts correctly and handles Exa cleanly."""
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Mocked Intent"))

    # We patch global_llm and exa_client to avoid real network calls
    with patch("ai_interview_coach.main.global_llm", mock_llm), \
         patch("ai_interview_coach.main.exa_client", None):
        
        result = await analyzer_node(mock_interview_state)
        
        # Verify the LLM was called
        mock_llm.ainvoke.assert_called_once()
        # Verify it returns the expected dictionary keys
        assert "intent_summary" in result
        assert "exa_research" in result
        assert result["intent_summary"] == "Mocked Intent"
        assert result["exa_research"] == "No external research needed."


@pytest.mark.asyncio
async def test_alternative_node_guardrails(mock_interview_state):
    """Test that alternative_node applies Regex and string constraints properly."""
    mock_llm = MagicMock()
    
    # Simulate the LLM returning unwanted roleplay formatting
    dirty_response = "*[Clears throat]* Narrator: Well, we thought about a monolith."
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content=dirty_response))

    with patch("ai_interview_coach.main.global_llm", mock_llm):
        result = await alternative_node(mock_interview_state)
        
        clean_response = result["alternatives"]
        
        # Guardrail 1: Roleplay tags should be stripped
        assert "*[Clears throat]*" not in clean_response
        assert "Narrator:" not in clean_response
        
        # Guardrail 2: Must enforce the starting phrase
        assert clean_response.lower().startswith("we considered")


# --- RUN_AGENT TESTS ---

@pytest.mark.asyncio
async def test_run_agent_empty_input():
    """Test that empty inputs are rejected before hitting the graph."""
    messages = [{"role": "user", "content": "   "}]
    
    result = await run_agent(messages)
    assert result == "Please provide an interview question."


@pytest.mark.asyncio
async def test_run_agent_truncates_long_input():
    """Test DoS protection: overly long inputs should be truncated."""
    long_string = "A" * 2000
    messages = [{"role": "user", "content": long_string}]
    
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value={"final_response": "Processed"})
    
    with patch("ai_interview_coach.main.graph", mock_graph), \
         patch("ai_interview_coach.main.mem0_client", None):
        
        await run_agent(messages)
        
        # Capture the arguments passed to ainvoke
        called_args = mock_graph.ainvoke.call_args[0][0]
        question_passed_to_graph = called_args["question"]
        
        # Verify it was truncated to 1500 chars + "..."
        assert len(question_passed_to_graph) == 1503
        assert question_passed_to_graph.endswith("...")


@pytest.mark.asyncio
async def test_run_agent_graph_failure():
    """Test that if the graph crashes, the user gets a graceful error."""
    messages = [{"role": "user", "content": "Valid question"}]
    
    mock_graph = MagicMock()
    # Simulate an API timeout or LangGraph crash
    mock_graph.ainvoke = AsyncMock(side_effect=Exception("API Timeout"))
    
    with patch("ai_interview_coach.main.graph", mock_graph), \
         patch("ai_interview_coach.main.mem0_client", None):
        
        result = await run_agent(messages)
        assert "Operational Error:" in result


# --- HANDLER TESTS ---

@pytest.mark.asyncio
async def test_handler_initialization_flow():
    """Test that the handler initializes globals on the first run."""
    messages = [{"role": "user", "content": "Test"}]
    
    # We patch _initialized to False to force the init block to run
    with patch("ai_interview_coach.main._initialized", False), \
         patch("ai_interview_coach.main.initialize_all", new_callable=AsyncMock) as mock_init, \
         patch("ai_interview_coach.main.run_agent", new_callable=AsyncMock, return_value="Success") as mock_run:
        
        result = await handler(messages)
        
        mock_init.assert_called_once()
        mock_run.assert_called_once_with(messages)
        assert result == "Success"