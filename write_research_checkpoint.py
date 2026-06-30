from lib.checkpoint import write_checkpoint
from pathlib import Path
import json

# Load research brief
with open("projects/brazil-vs-japan-world-cup-2026/artifacts/research_brief.json", "r", encoding="utf-8") as f:
    research_brief = json.load(f)

# Write checkpoint
write_checkpoint(
    pipeline_dir=Path("projects"),
    project_id="brazil-vs-japan-world-cup-2026",
    stage="research",
    status="completed",
    artifacts={"research_brief": research_brief},
    pipeline_type="animated-explainer",
    style_playbook="flat-motion-graphics",
)
print("SUCCESS: Checkpoint written!")
