"""Data models for Synq SDK."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class OutputFormatType(str, Enum):
    """Types of output formats available for sandbox results."""
    
    SUMMARY = "summary"
    DECISION = "decision"
    JSON = "json"
    CUSTOM = "custom"


@dataclass
class Agent:
    """Represents an AI agent in the Synq system."""
    
    id: str
    owner_id: str
    type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    state_dimensions: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Create an Agent from a dictionary."""
        return cls(
            id=data.get("id", ""),
            owner_id=data.get("owner_id", ""),
            type=data.get("type", ""),
            metadata=data.get("metadata", {}),
            state_dimensions=data.get("state_dimensions", {}),
            status=data.get("status", "active"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Agent to a dictionary."""
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "type": self.type,
            "metadata": self.metadata,
            "state_dimensions": self.state_dimensions,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class OutputFormat:
    """Defines the output format for a sandbox."""
    
    type: OutputFormatType
    instructions: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert OutputFormat to a dictionary."""
        result = {"type": self.type.value}
        if self.instructions:
            result["instructions"] = self.instructions
        if self.schema:
            result["schema"] = self.schema
        return result


@dataclass
class Sandbox:
    """Represents a sandbox environment where agents interact."""
    
    id: str
    agent_ids: List[str]
    ttl_seconds: int
    status: str = "active"
    context: Dict[str, Any] = field(default_factory=dict)
    output_format: Optional[OutputFormat] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sandbox":
        """Create a Sandbox from a dictionary."""
        output_format = None
        if "output_format" in data and data["output_format"]:
            of_data = data["output_format"]
            output_format = OutputFormat(
                type=OutputFormatType(of_data.get("type", "summary")),
                instructions=of_data.get("instructions"),
                schema=of_data.get("schema"),
            )
        
        return cls(
            id=data.get("id", ""),
            agent_ids=data.get("agent_ids", []),
            ttl_seconds=data.get("ttl_seconds", 3600),
            status=data.get("status", "active"),
            context=data.get("context", {}),
            output_format=output_format,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Sandbox to a dictionary."""
        result = {
            "id": self.id,
            "agent_ids": self.agent_ids,
            "ttl_seconds": self.ttl_seconds,
            "status": self.status,
            "context": self.context,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.output_format:
            result["output_format"] = self.output_format.to_dict()
        return result


@dataclass
class Message:
    """Represents a message in a sandbox conversation."""
    
    id: str
    from_agent_id: str
    to_agent_id: Optional[str]
    to_topic: Optional[str]
    type: str
    payload: Any
    timestamp: int
    sandbox_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create a Message from a dictionary."""
        return cls(
            id=data.get("id", ""),
            from_agent_id=data.get("from_agent_id", ""),
            to_agent_id=data.get("to_agent_id"),
            to_topic=data.get("to_topic"),
            type=data.get("type", ""),
            payload=data.get("payload"),
            timestamp=data.get("timestamp", 0),
            sandbox_id=data.get("sandbox_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Message to a dictionary."""
        return {
            "id": self.id,
            "from_agent_id": self.from_agent_id,
            "to_agent_id": self.to_agent_id,
            "to_topic": self.to_topic,
            "type": self.type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "sandbox_id": self.sandbox_id,
        }

