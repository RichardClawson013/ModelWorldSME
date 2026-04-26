"""
ModelWorldSME — Business world model elicitation library.

Apache 2.0 License — https://github.com/RichardClawson013/ModelWorldSME

One conversational interview. Three outputs:
  - Personalized world model JSON
  - Agent configuration YAML
  - Agent identity SOUL.md

Provider agnostic. Model agnostic. Orchestrator agnostic.

Quick start:
    from model_world_sme import InterviewFlow, default_worldmodel_path

    flow = InterviewFlow(worldmodel_path=default_worldmodel_path())
    question = flow.next()
    while question:
        answer = input(f"{question}\\n> ")
        question = flow.next(answer)
    result = flow.export()
"""

from pathlib import Path

from .interview.flow import InterviewFlow, InterviewResult


def default_worldmodel_path() -> Path:
    """Return the path to the bundled SME world model (v1.5, 2986 tasks)."""
    bundled = Path(__file__).parent / "worldmodel" / "sme_worldmodel_v1.5.json"
    if bundled.exists():
        return bundled
    # fallback for development installs
    repo_root = Path(__file__).parent.parent
    return repo_root / "worldmodel" / "sme_worldmodel_v1.5.json"


__version__ = "1.0.0"
__all__ = ["InterviewFlow", "InterviewResult", "default_worldmodel_path"]
