"""Augment SDK - Python client for Augment CLI agent"""

__version__ = "0.1.4"

from .agent import Auggie, Agent, Model, ModelType, VerificationResult
from .exceptions import (
    AugmentError,
    AugmentCLIError,
    AugmentJSONError,
    AugmentNotFoundError,
    AugmentParseError,
    AugmentWorkspaceError,
    AugmentVerificationError,
)
from .listener import AgentListener, LoggingAgentListener

__all__ = [
    "Auggie",
    "Agent",  # Backward compatibility
    "Model",
    "ModelType",
    "VerificationResult",
    "AgentListener",
    "LoggingAgentListener",
    "AugmentError",
    "AugmentCLIError",
    "AugmentJSONError",
    "AugmentNotFoundError",
    "AugmentParseError",
    "AugmentWorkspaceError",
    "AugmentVerificationError",
]
