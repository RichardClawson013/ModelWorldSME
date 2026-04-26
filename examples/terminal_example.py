"""
examples/terminal_example.py — Run a complete interview in your terminal.

No API key needed — matching is fully deterministic.
Run: python examples/terminal_example.py
"""

from model_world_sme import InterviewFlow, default_worldmodel_path


def main() -> None:
    flow = InterviewFlow(worldmodel_path=default_worldmodel_path())

    print("=" * 60)
    print("ModelWorldSME — Business Elicitation Interview")
    print("=" * 60)

    question = flow.next()
    while question:
        print(f"\n{question}")
        answer = input("> ").strip()
        if not answer:
            continue
        question = flow.next(answer)

    print("\n" + "=" * 60)
    print("Interview complete. Generating outputs...")

    result = flow.export()

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    agent_name = result.summary.get("agent_name", "assistant")
    (out_dir / f"worldmodel_{agent_name}.json").write_text(result.worldmodel_json, encoding="utf-8")
    (out_dir / f"agent_config_{agent_name}.yaml").write_text(result.agent_config_yaml, encoding="utf-8")
    (out_dir / f"SOUL_{agent_name}.md").write_text(result.soul_md, encoding="utf-8")

    print(f"  Tasks confirmed: {result.summary.get('total_active', 0)}")
    print(f"  Agent name:      {agent_name}")
    print(f"  Saved to:        output/")
    if result.warnings:
        print(f"  Warnings:        {len(result.warnings)} (see worldmodel JSON)")


if __name__ == "__main__":
    main()
