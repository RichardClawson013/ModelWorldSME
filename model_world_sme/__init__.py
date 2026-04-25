"""
ModelWorldSME — Business world model elicitation library.

Apache 2.0 License — https://github.com/RichardClawson013/ModelWorldSME

One conversational interview. Three outputs:
  - Personalized world model JSON
  - Agent configuration YAML
  - Agent identity SOUL.md

Provider agnostic. Model agnostic. Orchestrator agnostic.
"""

from .interview.flow import InterviewFlow, InterviewResult

__version__ = "1.0.0"
__all__ = ["InterviewFlow", "InterviewResult"]
