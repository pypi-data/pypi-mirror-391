"""Main client for interacting with the Synq API."""

import requests
from typing import Dict, List, Optional, Any
from .models import Agent, Sandbox, Message, OutputFormat
from .exceptions import SynqAPIError, SynqConnectionError, SynqValidationError


class SynqClient:
    """Client for interacting with the Synq Multi-Agent AI System API.
    
    Example:
        >>> client = SynqClient(base_url="http://localhost:8080")
        >>> agents = client.list_agents()
        >>> sandbox = client.create_sandbox(
        ...     sandbox_id="test_sandbox",
        ...     agent_ids=["agent1", "agent2"],
        ...     ttl_seconds=3600
        ... )
    """

    def __init__(self, base_url: str = "http://localhost:8080", timeout: int = 30):
        """Initialize the Synq client.
        
        Args:
            base_url: Base URL of the Synq API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an HTTP request to the Synq API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: JSON data to send in request body
            params: Query parameters
            
        Returns:
            Response data as dictionary or list
            
        Raises:
            SynqConnectionError: If connection fails
            SynqAPIError: If API returns an error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )
            
            # Check for HTTP errors
            if response.status_code >= 400:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"]
                except:
                    error_msg = response.text or error_msg
                
                raise SynqAPIError(
                    error_msg,
                    status_code=response.status_code,
                    response_body=response.text,
                )
            
            # Return JSON response if available
            if response.text:
                try:
                    return response.json()
                except ValueError:
                    return response.text
            
            return None
            
        except requests.ConnectionError as e:
            raise SynqConnectionError(f"Failed to connect to Synq API at {url}: {e}")
        except requests.Timeout as e:
            raise SynqConnectionError(f"Request to Synq API timed out: {e}")
        except requests.RequestException as e:
            raise SynqConnectionError(f"Request to Synq API failed: {e}")

    # Agent Management

    def list_agents(self) -> List[Agent]:
        """List all registered agents.
        
        Returns:
            List of Agent objects
        """
        data = self._request("GET", "/agents")
        if not data or "agents" not in data:
            return []
        return [Agent.from_dict(agent) for agent in data["agents"]]

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get a specific agent by ID.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            Agent object or None if not found
        """
        agents = self.list_agents()
        for agent in agents:
            if agent.id == agent_id:
                return agent
        return None

    # Sandbox Management

    def create_sandbox(
        self,
        sandbox_id: str,
        agent_ids: List[str],
        ttl_seconds: int = 3600,
        output_format: Optional[OutputFormat] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Sandbox:
        """Create a new sandbox for agents to interact in.
        
        Args:
            sandbox_id: Unique identifier for the sandbox
            agent_ids: List of agent IDs to include in the sandbox
            ttl_seconds: Time-to-live in seconds (default: 3600)
            output_format: Optional output format configuration
            context: Optional context metadata
            
        Returns:
            Created Sandbox object
            
        Raises:
            SynqValidationError: If inputs are invalid
            SynqAPIError: If API returns an error
        """
        if not sandbox_id:
            raise SynqValidationError("sandbox_id cannot be empty")
        if not agent_ids:
            raise SynqValidationError("agent_ids cannot be empty")
        if ttl_seconds <= 0:
            raise SynqValidationError("ttl_seconds must be positive")

        payload = {
            "id": sandbox_id,
            "agents": agent_ids,
            "ttl_seconds": ttl_seconds,
        }
        
        if output_format:
            payload["output_format"] = output_format.to_dict()
        
        if context:
            payload["context"] = context

        data = self._request("POST", "/sandbox/create", data=payload)
        
        # The API may return the sandbox data or just a success message
        if isinstance(data, dict) and "sandbox" in data:
            return Sandbox.from_dict(data["sandbox"])
        else:
            # Construct sandbox from request data
            return Sandbox(
                id=sandbox_id,
                agent_ids=agent_ids,
                ttl_seconds=ttl_seconds,
                status="active",
                output_format=output_format,
                context=context or {},
            )

    def list_sandboxes(self) -> List[Sandbox]:
        """List all active sandboxes.
        
        Returns:
            List of Sandbox objects
        """
        data = self._request("GET", "/sandboxes")
        if not data or "sandboxes" not in data:
            return []
        return [Sandbox.from_dict(sb) for sb in data["sandboxes"]]

    def get_sandbox(self, sandbox_id: str) -> Optional[Sandbox]:
        """Get a specific sandbox by ID.
        
        Args:
            sandbox_id: The sandbox's unique identifier
            
        Returns:
            Sandbox object or None if not found
        """
        sandboxes = self.list_sandboxes()
        for sandbox in sandboxes:
            if sandbox.id == sandbox_id:
                return sandbox
        return None

    def close_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """Close a sandbox, stopping all interactions.
        
        Args:
            sandbox_id: The sandbox's unique identifier
            
        Returns:
            Response data from the API
        """
        return self._request("POST", "/sandbox/close", data={"sandbox_id": sandbox_id})

    # Message Management

    def get_messages(self, sandbox_id: str) -> List[Message]:
        """Get all messages in a sandbox.
        
        Args:
            sandbox_id: The sandbox's unique identifier
            
        Returns:
            List of Message objects
        """
        data = self._request("GET", "/sandbox/messages", params={"id": sandbox_id})
        if not data or "messages" not in data:
            return []
        return [Message.from_dict(msg) for msg in data["messages"]]

    def agent_respond(
        self,
        sandbox_id: str,
        agent_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """Trigger a specific agent to respond to a message.
        
        Args:
            sandbox_id: The sandbox's unique identifier
            agent_id: The agent's unique identifier
            message: The message content
            
        Returns:
            Response data from the API
        """
        return self._request(
            "POST",
            "/sandbox/agent-respond",
            data={
                "sandbox_id": sandbox_id,
                "agent_id": agent_id,
                "message": message,
            },
        )

    def start_ai_conversation(
        self,
        sandbox_id: str,
        rounds: int = 5,
    ) -> Dict[str, Any]:
        """Start an automatic AI conversation between agents.
        
        Args:
            sandbox_id: The sandbox's unique identifier
            rounds: Number of conversation rounds (default: 5)
            
        Returns:
            Response data from the API
        """
        return self._request(
            "POST",
            "/sandbox/start-ai-conversation",
            data={
                "sandbox_id": sandbox_id,
                "rounds": rounds,
            },
        )

    def continue_conversation(
        self,
        sandbox_id: str,
        rounds: int = 3,
    ) -> Dict[str, Any]:
        """Continue an existing conversation for additional rounds.
        
        Args:
            sandbox_id: The sandbox's unique identifier
            rounds: Number of additional conversation rounds (default: 3)
            
        Returns:
            Response data from the API
        """
        return self._request(
            "POST",
            "/sandbox/continue-conversation",
            data={
                "sandbox_id": sandbox_id,
                "rounds": rounds,
            },
        )

    # Output Generation

    def generate_output(self, sandbox_id: str) -> Dict[str, Any]:
        """Generate formatted output from a sandbox conversation.
        
        Args:
            sandbox_id: The sandbox's unique identifier
            
        Returns:
            Generated output data
        """
        return self._request(
            "GET",
            "/sandbox/generate-output",
            params={"sandbox_id": sandbox_id},
        )

    # Vector Search

    def vector_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for similar agents using vector embeddings.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of similar agents with scores
        """
        data = self._request(
            "POST",
            "/vector/search",
            data={
                "query_vector": query_vector,
                "top_k": top_k,
            },
        )
        return data.get("results", [])

    # Health Check

    def health_check(self) -> Dict[str, Any]:
        """Check if the Synq API is healthy.
        
        Returns:
            Health status data
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return {"status": "healthy" if response.status_code == 200 else "unhealthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

