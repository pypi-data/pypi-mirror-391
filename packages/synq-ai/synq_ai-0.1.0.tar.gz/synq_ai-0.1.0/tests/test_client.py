"""Unit tests for Synq Python SDK client."""

import pytest
from unittest.mock import Mock, patch
from synq import SynqClient
from synq.models import Agent, Sandbox, Message, OutputFormat, OutputFormatType
from synq.exceptions import (
    SynqAPIError,
    SynqConnectionError,
    SynqValidationError,
)


class TestSynqClient:
    """Tests for SynqClient class."""

    def test_client_initialization(self):
        """Test client initialization with default and custom parameters."""
        # Default initialization
        client = SynqClient()
        assert client.base_url == "http://localhost:8080"
        assert client.timeout == 30

        # Custom initialization
        client = SynqClient(base_url="http://example.com:9000", timeout=60)
        assert client.base_url == "http://example.com:9000"
        assert client.timeout == 60

    def test_base_url_trailing_slash(self):
        """Test that trailing slashes are removed from base_url."""
        client = SynqClient(base_url="http://localhost:8080/")
        assert client.base_url == "http://localhost:8080"

    @patch("synq.client.requests.Session.request")
    def test_list_agents_success(self, mock_request):
        """Test listing agents successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agents": [
                {
                    "id": "agent1",
                    "owner_id": "owner1",
                    "type": "openai",
                    "metadata": {},
                    "state_dimensions": {},
                    "status": "active",
                }
            ]
        }
        mock_request.return_value = mock_response

        client = SynqClient()
        agents = client.list_agents()

        assert len(agents) == 1
        assert isinstance(agents[0], Agent)
        assert agents[0].id == "agent1"
        assert agents[0].type == "openai"

    @patch("synq.client.requests.Session.request")
    def test_list_agents_empty(self, mock_request):
        """Test listing agents when none exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"agents": []}
        mock_request.return_value = mock_response

        client = SynqClient()
        agents = client.list_agents()

        assert len(agents) == 0

    def test_create_sandbox_validation(self):
        """Test sandbox creation validation."""
        client = SynqClient()

        # Empty sandbox_id
        with pytest.raises(SynqValidationError, match="sandbox_id cannot be empty"):
            client.create_sandbox(
                sandbox_id="",
                agent_ids=["agent1"],
                ttl_seconds=3600,
            )

        # Empty agent_ids
        with pytest.raises(SynqValidationError, match="agent_ids cannot be empty"):
            client.create_sandbox(
                sandbox_id="test",
                agent_ids=[],
                ttl_seconds=3600,
            )

        # Invalid ttl_seconds
        with pytest.raises(SynqValidationError, match="ttl_seconds must be positive"):
            client.create_sandbox(
                sandbox_id="test",
                agent_ids=["agent1"],
                ttl_seconds=0,
            )

    @patch("synq.client.requests.Session.request")
    def test_create_sandbox_success(self, mock_request):
        """Test creating a sandbox successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "created"}
        mock_response.text = '{"status": "created"}'
        mock_request.return_value = mock_response

        client = SynqClient()
        sandbox = client.create_sandbox(
            sandbox_id="test_sandbox",
            agent_ids=["agent1", "agent2"],
            ttl_seconds=3600,
        )

        assert isinstance(sandbox, Sandbox)
        assert sandbox.id == "test_sandbox"
        assert sandbox.agent_ids == ["agent1", "agent2"]
        assert sandbox.ttl_seconds == 3600

    @patch("synq.client.requests.Session.request")
    def test_create_sandbox_with_output_format(self, mock_request):
        """Test creating a sandbox with output format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "created"}
        mock_response.text = '{"status": "created"}'
        mock_request.return_value = mock_response

        client = SynqClient()
        output_format = OutputFormat(
            type=OutputFormatType.SUMMARY,
            instructions="Summarize the conversation",
        )
        
        sandbox = client.create_sandbox(
            sandbox_id="test_sandbox",
            agent_ids=["agent1", "agent2"],
            ttl_seconds=3600,
            output_format=output_format,
        )

        assert sandbox.output_format is not None
        assert sandbox.output_format.type == OutputFormatType.SUMMARY
        assert sandbox.output_format.instructions == "Summarize the conversation"

    @patch("synq.client.requests.Session.request")
    def test_api_error_handling(self, mock_request):
        """Test handling of API errors."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_response.text = '{"error": "Invalid request"}'
        mock_request.return_value = mock_response

        client = SynqClient()
        
        with pytest.raises(SynqAPIError) as exc_info:
            client.list_agents()
        
        assert exc_info.value.status_code == 400
        assert "Invalid request" in str(exc_info.value)

    @patch("synq.client.requests.Session.request")
    def test_connection_error_handling(self, mock_request):
        """Test handling of connection errors."""
        import requests
        mock_request.side_effect = requests.ConnectionError("Connection failed")

        client = SynqClient()
        
        with pytest.raises(SynqConnectionError):
            client.list_agents()

    @patch("synq.client.requests.Session.request")
    def test_get_messages(self, mock_request):
        """Test getting messages from a sandbox."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [
                {
                    "id": "msg1",
                    "from_agent_id": "agent1",
                    "to_agent_id": "agent2",
                    "type": "chat",
                    "payload": {"content": "Hello"},
                    "timestamp": 1234567890,
                }
            ]
        }
        mock_request.return_value = mock_response

        client = SynqClient()
        messages = client.get_messages(sandbox_id="test_sandbox")

        assert len(messages) == 1
        assert isinstance(messages[0], Message)
        assert messages[0].id == "msg1"
        assert messages[0].from_agent_id == "agent1"

    @patch("synq.client.requests.Session.request")
    def test_agent_respond(self, mock_request):
        """Test triggering an agent response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "sent"}
        mock_response.text = '{"status": "sent"}'
        mock_request.return_value = mock_response

        client = SynqClient()
        result = client.agent_respond(
            sandbox_id="test_sandbox",
            agent_id="agent1",
            message="Hello",
        )

        assert result["status"] == "sent"
        
        # Verify request was made with correct parameters
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["json"]["sandbox_id"] == "test_sandbox"
        assert call_args[1]["json"]["agent_id"] == "agent1"
        assert call_args[1]["json"]["message"] == "Hello"

    @patch("synq.client.requests.Session.request")
    def test_start_ai_conversation(self, mock_request):
        """Test starting an AI conversation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "started"}
        mock_response.text = '{"status": "started"}'
        mock_request.return_value = mock_response

        client = SynqClient()
        result = client.start_ai_conversation(
            sandbox_id="test_sandbox",
            rounds=5,
        )

        assert result["status"] == "started"

    @patch("synq.client.requests.Session.request")
    def test_generate_output(self, mock_request):
        """Test generating formatted output."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": "This is a summary of the conversation."
        }
        mock_request.return_value = mock_response

        client = SynqClient()
        output = client.generate_output(sandbox_id="test_sandbox")

        assert "output" in output
        assert output["output"] == "This is a summary of the conversation."

    @patch("synq.client.requests.Session.request")
    def test_close_sandbox(self, mock_request):
        """Test closing a sandbox."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "closed"}
        mock_response.text = '{"status": "closed"}'
        mock_request.return_value = mock_response

        client = SynqClient()
        result = client.close_sandbox(sandbox_id="test_sandbox")

        assert result["status"] == "closed"


class TestModels:
    """Tests for data models."""

    def test_agent_from_dict(self):
        """Test creating Agent from dictionary."""
        data = {
            "id": "agent1",
            "owner_id": "owner1",
            "type": "openai",
            "metadata": {"key": "value"},
            "state_dimensions": {"dim": 1},
            "status": "active",
        }
        
        agent = Agent.from_dict(data)
        
        assert agent.id == "agent1"
        assert agent.owner_id == "owner1"
        assert agent.type == "openai"
        assert agent.metadata == {"key": "value"}

    def test_sandbox_from_dict(self):
        """Test creating Sandbox from dictionary."""
        data = {
            "id": "sandbox1",
            "agent_ids": ["agent1", "agent2"],
            "ttl_seconds": 3600,
            "status": "active",
        }
        
        sandbox = Sandbox.from_dict(data)
        
        assert sandbox.id == "sandbox1"
        assert sandbox.agent_ids == ["agent1", "agent2"]
        assert sandbox.ttl_seconds == 3600

    def test_output_format_to_dict(self):
        """Test converting OutputFormat to dictionary."""
        output_format = OutputFormat(
            type=OutputFormatType.JSON,
            instructions="Test instructions",
            schema={"field": "value"},
        )
        
        data = output_format.to_dict()
        
        assert data["type"] == "json"
        assert data["instructions"] == "Test instructions"
        assert data["schema"] == {"field": "value"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

