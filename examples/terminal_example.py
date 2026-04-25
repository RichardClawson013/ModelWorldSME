"""
examples/terminal_example.py — Run a complete interview in your terminal.

No API key needed for the matching — only if you want AI-generated questions.
Run: python examples/terminal_example.py
"""

import asyncio
import json
from pathlib import Path

from model_world_sme import InterviewFlow
from model_world_sme.orchestrators import TerminalOrchestrator


async def main() -> None:
    worldmodel = Path(__file__).parent.parent / "worldmodel" / "sme_worldmodel_v1.5.json"

    flow = InterviewFlow(worldmodel_path=worldmodel)
    orchestrator = TerminalOrchestrator()

    print("=" * 60)
    print("ModelWorldSME — Business Elicitation Interview")
    print("=" * 60)

    async for question in flow.questions():
        answer = await orchestrator.send(question)
        flow.answer(answer)

    result = flow.export()
    await orchestrator.on_complete(result)

    # Save outputs
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    agent_name = result.summary.get("agent_name", "assistant")
    (out_dir / f"worldmodel_{agent_name}.json").write_text(result.worldmodel_json, encoding="utf-8")
    (out_dir / f"agent_config_{agent_name}.yaml").write_text(result.agent_config_yaml, encoding="utf-8")
    (out_dir / f"SOUL_{agent_name}.md").write_text(result.soul_md, encoding="utf-8")

    print(f"\nSaved to output/")


if __name__ == "__main__":
    asyncio.run(main())
