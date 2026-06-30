import json
import shutil
import subprocess
from pathlib import Path

# 1. Copy the assets to the remotion-composer public directory
src_assets = Path("projects/brazil-vs-japan-world-cup-2026/assets")
dst_assets = Path("remotion-composer/public/projects/brazil-vs-japan-world-cup-2026/assets")
dst_assets.mkdir(parents=True, exist_ok=True)

print("Copying assets to public directory...")
shutil.copytree(src_assets, dst_assets, dirs_exist_ok=True)

# 2. Load the generated edit_decisions, asset_manifest, and script
project_dir = Path("projects/brazil-vs-japan-world-cup-2026")
artifacts_dir = project_dir / "artifacts"

with open(artifacts_dir / "edit_decisions.json", "r", encoding="utf-8") as f:
    edit_decisions = json.load(f)

with open(artifacts_dir / "asset_manifest.json", "r", encoding="utf-8") as f:
    asset_manifest = json.load(f)

with open(artifacts_dir / "script.json", "r", encoding="utf-8") as f:
    script = json.load(f)

asset_lookup = {a["id"]: a for a in asset_manifest.get("assets", [])}

# Build sequential cuts and word-level captions
cuts = []
captions = []
current_time = 0.0

for scene in asset_manifest["assets"]:
    if scene["type"] == "image":
        scene_id = scene["scene_id"]
        # Find corresponding narration duration
        narration_asset = next(a for a in asset_manifest["assets"] if a["type"] == "narration" and a["scene_id"] == scene_id)
        duration = narration_asset["duration_seconds"]
        
        # Sequenced cuts
        cuts.append({
            "id": f"cut_{scene_id}",
            "source": f"projects/brazil-vs-japan-world-cup-2026/assets/images/img_{scene_id}.png",
            "in_seconds": current_time,
            "out_seconds": current_time + duration,
            "speed": 1.0
        })
        
        # Word-level captions
        # Find script section text
        sec_id = f"s{scene_id[2:]}" # sc1 -> s1_hook, sc2 -> s2_october_blueprint, etc.
        section = next(s for s in script["sections"] if s["id"].startswith(sec_id))
        words = section["text"].split()
        word_dur_ms = (duration * 1000) / len(words)
        
        current_ms = current_time * 1000
        for w in words:
            captions.append({
                "word": w,
                "startMs": int(current_ms),
                "endMs": int(current_ms + word_dur_ms)
            })
            current_ms += word_dur_ms
            
        current_time += duration

# Setup props
props = {
    "version": "1.0",
    "render_runtime": "remotion",
    "renderer_family": "explainer-data",
    "cuts": cuts,
    "captions": captions,
    "audio": {
        "narration": {
            "src": "projects/brazil-vs-japan-world-cup-2026/assets/narration_concat.wav",
            "volume": 1.0
        },
        "music": {
            "src": "projects/brazil-vs-japan-world-cup-2026/assets/music_bg.mp3",
            "volume": 0.15,
            "fadeInSeconds": 1.0,
            "fadeOutSeconds": 2.0
        }
    },
    "subtitles": {
        "enabled": False # Using Remotion CaptionOverlay instead
    }
}

# Write props
props_path = project_dir / "renders" / ".remotion_props_test.json"
props_path.parent.mkdir(parents=True, exist_ok=True)
with open(props_path, "w", encoding="utf-8") as f:
    json.dump(props, f, indent=2)

composer_dir = Path("remotion-composer").resolve()
cmd = [
    "npx", "remotion", "render",
    str(composer_dir / "src" / "index.tsx"),
    "Explainer",
    str((project_dir / "renders" / "final.mp4").resolve()),
    f"--props={props_path.resolve()}"
]

print("Running command:", " ".join(cmd))
res = subprocess.run(cmd, cwd=composer_dir, capture_output=True, text=True, shell=True)
print("\n--- STDOUT ---")
print(res.stdout)
print("\n--- STDERR ---")
print(res.stderr)
print("\n--- RETURN CODE ---")
print(res.returncode)
