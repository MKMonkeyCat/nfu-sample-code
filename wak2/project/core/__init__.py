"""Compatibility facade for core operations.

Public API remains available from this module while implementations are split
into smaller files to keep each file maintainable.
"""

from project.core.analysis import VoteAnalysisService
from project.core.storage import VoteCoreSystem


class VoteCoreService:
    """Facade service that composes storage and analysis services."""

    def __init__(self) -> None:
        self.storage = VoteCoreSystem()
        self.analysis = VoteAnalysisService()


__all__ = ["VoteCoreSystem", "VoteCoreService", "VoteAnalysisService"]
