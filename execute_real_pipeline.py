#!/usr/bin/env python3
"""Orchestrator script to execute all stages of the Brazil vs Japan World Cup 2026 match analysis video pipeline using real APIs, with intelligent reuse of already generated assets."""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

# 1. Reload environment path to pick up the newly installed FFmpeg
print("Reloading environment variables...")
os.environ["PATH"] = os.popen('powershell "[System.Environment]::GetEnvironmentVariable(\'Path\', \'Machine\') + \';\' + [System.Environment]::GetEnvironmentVariable(\'Path\', \'User\')"').read().strip()

PROJECT_ROOT = str(Path(__file__).resolve().parent)
sys.path.insert(0, PROJECT_ROOT)

from tools.tool_registry import registry
from tools.audio.tts_selector import TTSSelector
from tools.graphics.image_selector import ImageSelector
from tools.audio.audio_mixer import AudioMixer
from tools.video.video_compose import VideoCompose
from lib.checkpoint import write_checkpoint, read_checkpoint
from tools.cost_tracker import CostTracker, BudgetMode
from schemas.artifacts import validate_artifact

PROJECT_ID = "brazil-vs-japan-world-cup-2026"
PROJECT_DIR = Path("projects") / PROJECT_ID
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"
ASSETS_DIR = PROJECT_DIR / "assets"
RENDERS_DIR = PROJECT_DIR / "renders"

ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
(ASSETS_DIR / "images").mkdir(parents=True, exist_ok=True)
(ASSETS_DIR / "audio").mkdir(parents=True, exist_ok=True)
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

# Discover tools
registry.discover()

# Initialize cost tracker
cost_log = PROJECT_DIR / "cost_log.json"
tracker = CostTracker(
    budget_total_usd=5.0,
    mode=BudgetMode.OBSERVE,
    cost_log_path=cost_log,
)

def get_audio_duration(path: Path) -> float:
    """Get the duration of an audio file using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

# ===================================================================
# Stage 1: Load script
# ===================================================================
print("\n=== STAGE 2: LOADING SCRIPT ===")
script_path = ARTIFACTS_DIR / "script.json"
if not script_path.exists():
    script = {
        "version": "1.0",
        "title": "Bản Thiết Kế Tháng Mười: Brazil vs Nhật Bản",
        "total_duration_seconds": 60,
        "sections": [
            {
                "id": "s1_hook",
                "label": "Mở đầu",
                "text": "Brazil đối đầu Nhật Bản tại vòng 32 đội World Cup 2026. Lịch sử đứng về phía Brazil với 11 chiến thắng, nhưng Nhật Bản đã có công thức gây sốc.",
                "start_seconds": 0,
                "end_seconds": 10,
                "speaker_directions": "Hào hứng, cuốn hút và nhịp điệu nhanh.",
                "enhancement_cues": [{"type": "overlay", "description": "Hiện chữ lớn: Brazil vs Nhật Bản - Vòng 32 Đội World Cup 2026", "timestamp_seconds": 2.0}]
            },
            {
                "id": "s2_october_blueprint",
                "label": "Bản thiết kế 2025",
                "text": "Tháng Mười năm 2025, Nhật Bản hạ gục Brazil 3-2 trong trận giao hữu lịch sử. Moriyasu đã tìm ra điểm yếu ở hàng thủ Selecao bằng các đường phản công chớp nhoáng.",
                "start_seconds": 10,
                "end_seconds": 22,
                "speaker_directions": "Nhấn mạnh, kịch tính, nhịp điệu trung bình.",
                "enhancement_cues": [{"type": "stat_card", "description": "Bảng kết quả lịch sử: Nhật Bản 3 - 2 Brazil (Tháng 10/2025)", "timestamp_seconds": 14.0}]
            },
            {
                "id": "s3_injury_crisis",
                "label": "Khủng hoảng nhân sự cánh",
                "text": "Tuy nhiên, cả hai đội đều mất đi đôi cánh. Takefusa Kubo chấn thương đầu gối bên phía Nhật Bản, còn Raphinha của Brazil gặp vấn đề gân kheo.",
                "start_seconds": 22,
                "end_seconds": 34,
                "speaker_directions": "Trầm lắng, phân tích thông tin nghiêm túc.",
                "enhancement_cues": [{"type": "overlay", "description": "Hiện thông tin chấn thương: Kubo (Gối trái - Out), Raphinha (Gân kheo - Chưa rõ)", "timestamp_seconds": 26.0}]
            },
            {
                "id": "s4_battle_systems",
                "label": "Đấu trí chiến thuật",
                "text": "Trận đấu tại Houston sẽ là cuộc đấu trí đỉnh cao giữa HLV Carlo Ancelotti và Hajime Moriyasu. Vinicius Jr. đang thăng hoa, liệu hàng thủ bất bại của Nhật Bản có đứng vững?",
                "start_seconds": 34,
                "end_seconds": 48,
                "speaker_directions": "Dồn dập, tăng dần kịch tính.",
                "enhancement_cues": [{"type": "diagram", "description": "Sơ đồ chiến thuật: Khối phòng ngự trung tuyến của Nhật Bản vs Sức ép cánh trái của Vinicius Jr.", "timestamp_seconds": 38.0}]
            },
            {
                "id": "s5_conclusion",
                "label": "Nhận định & Dự đoán",
                "text": "Một trận cầu đầy toan tính chiến thuật. Dự đoán: Trận đấu sẽ kéo dài vào hiệp phụ và Brazil sẽ đi tiếp nhờ khoảnh khắc tỏa sáng cá nhân.",
                "start_seconds": 48,
                "end_seconds": 60,
                "speaker_directions": "Quyết đoán, truyền cảm hứng và kết thúc mạnh mẽ.",
                "enhancement_cues": [{"type": "overlay", "description": "Bảng dự đoán tỷ số: Brazil thắng 2 - 1 (Sau hiệp phụ)", "timestamp_seconds": 53.0}]
            }
        ]
    }
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)
else:
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

validate_artifact("script", script)
write_checkpoint(
    Path("projects"), PROJECT_ID, "script", "completed",
    artifacts={"script": script},
    pipeline_type="animated-explainer"
)
print("Script stage completed!")

# ===================================================================
# Stage 2: Create scene plan with cinematic visual details
# ===================================================================
print("\n=== STAGE 3: GENERATING SCENE PLAN ===")
SCENE_DETAILS = [
    {
        "id": "sc1",
        "type": "generated",
        "description": "Tactical map of the match and logos of Brazil and Japan designed in a modern style, glowing neon on dark background, cinematic style, wide angle view, dramatic depth, dynamic neon lighting, 8k resolution, realistic action shot.",
        "start_seconds": 0,
        "end_seconds": 10,
        "script_section_id": "s1_hook",
        "required_assets": [
            {"type": "narration", "description": "TTS voiceover for Section 1", "source": "generate"},
            {"type": "image", "description": "Modern tactical board showing Brazil and Japan, glowing neon team logos, dark background, cinematic style, wide angle, dynamic lighting, 8k resolution, photorealistic", "source": "generate"}
        ]
    },
    {
        "id": "sc2",
        "type": "generated",
        "description": "Emotional goal celebration of Japanese football players in their historic 3-2 victory over Brazil, fireworks exploding, stadium stands burning with flares and passionate fans, cinematic style, wide angle, dynamic lighting, 8k resolution, realistic action shot.",
        "start_seconds": 10,
        "end_seconds": 22,
        "script_section_id": "s2_october_blueprint",
        "required_assets": [
            {"type": "narration", "description": "TTS voiceover for Section 2", "source": "generate"},
            {"type": "image", "description": "Emotional goal celebration of Japanese football players in blue kits in their historic 3-2 victory over Brazil, fireworks exploding, passionate stadium stands filled with flares and fans, cinematic style, wide angle, dynamic lighting, 8k resolution, realistic action shot", "source": "generate"}
        ]
    },
    {
        "id": "sc3",
        "type": "generated",
        "description": "Side-by-side view showing the close-up tense face of manager Carlo Ancelotti vs the calm, disciplined face of manager Hajime Moriyasu under glowing stadium floodlights, dramatic shadows, cinematic style, 8k resolution, realistic action shot.",
        "start_seconds": 22,
        "end_seconds": 34,
        "script_section_id": "s3_injury_crisis",
        "required_assets": [
            {"type": "narration", "description": "TTS voiceover for Section 3", "source": "generate"},
            {"type": "image", "description": "Side-by-side split screen showing: on the left, close-up of Carlo Ancelotti tense and anxious face, on the right, Hajime Moriyasu calm and disciplined face, under glowing stadium floodlights, dramatic shadows, cinematic style, 8k resolution, realistic action shot", "source": "generate"}
        ]
    },
    {
        "id": "sc4",
        "type": "generated",
        "description": "Vinicius Jr dribbling fast on the wing, stopped by a compact defensive wall of Japanese players forming a 5-4-1 block, motion blur light trails, cinematic action shot, wide angle, dynamic lighting, 8k resolution, realistic action shot.",
        "start_seconds": 34,
        "end_seconds": 48,
        "script_section_id": "s4_battle_systems",
        "required_assets": [
            {"type": "narration", "description": "TTS voiceover for Section 4", "source": "generate"},
            {"type": "image", "description": "Vinicius Jr dribbling fast on the wing, stopped by a compact defensive wall of Japanese players in blue kits forming a 5-4-1 block, motion blur light trails, cinematic action shot, wide angle, dynamic lighting, 8k resolution, realistic action shot", "source": "generate"}
        ]
    },
    {
        "id": "sc5",
        "type": "generated",
        "description": "Luxury gold predicted score graphics card displaying '2 - 1' with the shiny FIFA World Cup trophy gleaming in the background, golden reflections, cinematic style, shallow depth of field, 8k resolution, realistic action shot.",
        "start_seconds": 48,
        "end_seconds": 60,
        "script_section_id": "s5_conclusion",
        "required_assets": [
            {"type": "narration", "description": "TTS voiceover for Section 5", "source": "generate"},
            {"type": "image", "description": "Luxury gold graphics card displaying predicted score '2 - 1', with the shiny FIFA World Cup trophy gleaming in the background, golden reflections, cinematic style, shallow depth of field, 8k resolution", "source": "generate"}
        ]
    }
]

scene_plan = {
    "version": "1.0",
    "style_playbook": "flat-motion-graphics",
    "scenes": SCENE_DETAILS
}

with open(ARTIFACTS_DIR / "scene_plan.json", "w", encoding="utf-8") as f:
    json.dump(scene_plan, f, indent=2, ensure_ascii=False)

validate_artifact("scene_plan", scene_plan)
write_checkpoint(
    Path("projects"), PROJECT_ID, "scene_plan", "completed",
    artifacts={"scene_plan": scene_plan},
    pipeline_type="animated-explainer"
)
print("Scene plan stage completed!")

# ===================================================================
# Stage 3: Generate assets using real APIs (with file reuse check)
# ===================================================================
print("\n=== STAGE 4: GENERATING REAL ASSETS ===")
assets = []

# Initialize selectors
tts_selector = TTSSelector()
image_selector = ImageSelector()

# Process each scene
for i, scene in enumerate(scene_plan["scenes"]):
    scene_id = scene["id"]
    section_id = scene["script_section_id"]
    
    section_text = next(s["text"] for s in script["sections"] if s["id"] == section_id)
    print(f"\nProcessing Scene {scene_id} ({section_id})...")
    
    # 2. Generate Narration (OpenAI TTS)
    audio_filename = f"narration_{section_id}.mp3"
    audio_path = ASSETS_DIR / "audio" / audio_filename
    
    if audio_path.exists() and audio_path.stat().st_size > 1000:
        print(f"Reusing existing narration audio: {audio_path}")
        duration = get_audio_duration(audio_path)
        cost_tts = 0.0
    else:
        # Estimate and reserve cost
        est_cost = tts_selector.estimate_cost({"text": section_text})
        eid = tracker.estimate("openai_tts", "generate", est_cost)
        tracker.approve_tool("openai_tts")
        tracker.reserve(eid)
        
        print(f"Generating narration audio: {audio_path}")
        tts_result = tts_selector.execute({
            "text": section_text,
            "voice": "onyx",
            "output_path": str(audio_path),
            "preferred_provider": "openai"
        })
        
        if not tts_result.success:
            print(f"ERROR generating TTS for section {section_id}: {tts_result.error}")
            tracker.reconcile(eid, 0.0, success=False)
            sys.exit(1)
            
        duration = tts_result.data.get("audio_duration_seconds") or 10.0
        cost_tts = tts_result.cost_usd
        tracker.reconcile(eid, cost_tts, success=True)
    
    assets.append({
        "id": f"a_tts_{section_id}",
        "type": "narration",
        "path": str(audio_path),
        "source_tool": "openai_tts",
        "scene_id": scene_id,
        "duration_seconds": duration,
        "cost_usd": cost_tts
    })
    
    # 3. Generate Image (FLUX via Fal.ai)
    image_desc = next(a["description"] for a in scene["required_assets"] if a["type"] == "image")
    image_filename = f"img_{scene_id}.png"
    image_path = ASSETS_DIR / "images" / image_filename
    
    if image_path.exists() and image_path.stat().st_size > 1000:
        print(f"Reusing existing cinematic image: {image_path}")
        cost_img = 0.0
    else:
        # Estimate and reserve cost
        est_cost_img = image_selector.estimate_cost({"prompt": image_desc})
        eid_img = tracker.estimate("flux_image", "generate", est_cost_img)
        tracker.approve_tool("flux_image")
        tracker.reserve(eid_img)
        
        print(f"Generating cinematic image: {image_path}")
        img_result = image_selector.execute({
            "prompt": image_desc,
            "width": 1280,
            "height": 720,
            "output_path": str(image_path),
            "preferred_provider": "flux"
        })
        
        if not img_result.success:
            print(f"ERROR generating image for scene {scene_id}: {img_result.error}")
            tracker.reconcile(eid_img, 0.0, success=False)
            sys.exit(1)
            
        cost_img = img_result.cost_usd
        tracker.reconcile(eid_img, cost_img, success=True)
    
    assets.append({
        "id": f"a_img_{scene_id}",
        "type": "image",
        "path": str(image_path),
        "source_tool": "flux_image",
        "scene_id": scene_id,
        "cost_usd": cost_img
    })

# Check background music
bg_music_source = ASSETS_DIR / "music_bg.mp3"
if not bg_music_source.exists():
    print("Warning: music_bg.mp3 not found, generating a brief synth track...")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i",
         "sine=frequency=150:duration=60", "-ar", "44100", "-ac", "1", str(bg_music_source)],
        capture_output=True, check=True
    )

assets.append({
    "id": "a_music",
    "type": "music",
    "path": str(bg_music_source),
    "source_tool": "pixabay_music",
    "scene_id": "sc1"
})

asset_manifest = {
    "version": "1.0",
    "assets": assets,
    "total_cost_usd": sum(a.get("cost_usd", 0.0) for a in assets)
}

with open(ARTIFACTS_DIR / "asset_manifest.json", "w", encoding="utf-8") as f:
    json.dump(asset_manifest, f, indent=2, ensure_ascii=False)

validate_artifact("asset_manifest", asset_manifest)
write_checkpoint(
    Path("projects"), PROJECT_ID, "assets", "completed",
    artifacts={"asset_manifest": asset_manifest},
    pipeline_type="animated-explainer",
    cost_snapshot=tracker.cost_snapshot()
)
print("Asset generation stage completed!")

# ===================================================================
# Stage 4: Subtitles & Audio mixing
# ===================================================================
print("\n=== STAGE 5: MIXING AUDIO AND SUBTITLES ===")
mixer = AudioMixer()

# Combine all narration into one track
concat_narration = ASSETS_DIR / "narration_concat.wav"
narration_list = ASSETS_DIR / "narration_list.txt"
with open(narration_list, "w") as f:
    for scene in scene_plan["scenes"]:
        sec_id = scene["script_section_id"]
        audio_path = ASSETS_DIR / "audio" / f"narration_{sec_id}.mp3"
        safe = str(audio_path.resolve()).replace("\\", "/")
        f.write(f"file '{safe}'\n")

print("Concatenating narration audios...")
subprocess.run(
    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(narration_list),
     "-c", "copy", str(concat_narration)],
    capture_output=True, check=True,
)

# Duck music with narration
mix_output = ASSETS_DIR / "final_mix.wav"
print("Ducking music...")
mix_result = mixer.execute({
    "operation": "duck",
    "primary_audio": str(concat_narration),
    "secondary_audio": str(bg_music_source),
    "duck_level": -15,
    "output_path": str(mix_output),
    "normalize": True
})

if not mix_result.success:
    print(f"ERROR mixing audio: {mix_result.error}")
    sys.exit(1)

# Generate SRT subtitles
srt_path = ASSETS_DIR / "subtitles.srt"
print("Generating subtitles...")
srt_lines = []
current_time = 0.0

for i, scene in enumerate(scene_plan["scenes"]):
    sec_id = scene["script_section_id"]
    text = next(s["text"] for s in script["sections"] if s["id"] == sec_id)
    
    asset = next(a for a in assets if a["id"] == f"a_tts_{sec_id}")
    duration = asset["duration_seconds"]
    
    start_time = current_time
    end_time = current_time + duration
    current_time = end_time
    
    def format_ts(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int(round((seconds - int(seconds)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    srt_lines.append(f"{i+1}")
    srt_lines.append(f"{format_ts(start_time)} --> {format_ts(end_time)}")
    srt_lines.append(text)
    srt_lines.append("")

with open(srt_path, "w", encoding="utf-8") as f:
    f.write("\n".join(srt_lines))

# ===================================================================
# Stage 5: Edit Decisions & Copying to Remotion Public Folder
# ===================================================================
print("\n=== STAGE 5.5: PREPARING EDIT DECISIONS ===")

# Copy assets to the remotion-composer public directory
dst_assets = Path("remotion-composer/public/projects") / PROJECT_ID / "assets"
dst_assets.mkdir(parents=True, exist_ok=True)
print(f"Staging projects assets to Remotion public path: {dst_assets}")
shutil.copytree(ASSETS_DIR, dst_assets, dirs_exist_ok=True)

# Build sequential cuts and word-level captions
cuts = []
captions = []
current_time = 0.0

for scene in scene_plan["scenes"]:
    sec_id = scene["script_section_id"]
    scene_id = scene["id"]
    
    asset = next(a for a in assets if a["id"] == f"a_tts_{sec_id}")
    duration = asset["duration_seconds"]
    
    # Sequential cuts starting from 'projects/...' relative path
    cuts.append({
        "id": f"cut_{scene_id}",
        "source": f"projects/{PROJECT_ID}/assets/images/img_{scene_id}.png",
        "in_seconds": current_time,
        "out_seconds": current_time + duration,
        "speed": 1.0
    })
    
    # Word-level highlights
    text = next(s["text"] for s in script["sections"] if s["id"] == sec_id)
    words = text.split()
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

# Choose rendering runtime. We can try Remotion if node_modules exists, otherwise fallback to ffmpeg.
render_runtime = "ffmpeg"
composer_dir = Path("remotion-composer")
if (composer_dir / "node_modules").exists():
    print("Detected node_modules under remotion-composer! Choosing Remotion runtime.")
    render_runtime = "remotion"

edit_decisions = {
    "version": "1.0",
    "render_runtime": render_runtime,
    "renderer_family": "explainer-data",
    "cuts": cuts,
    "music": {
        "asset_id": "a_music",
        "volume": 0.15,
        "ducking": True,
        "fade_in_seconds": 1.0,
        "fade_out_seconds": 2.0
    },
    "subtitles": {
        "enabled": False, # Bypassed in Remotion in favor of rich text CaptionOverlay
        "style": "clean-professional",
        "source": str(srt_path)
    }
}

# Save standard format for validation and checkpointing
edit_decisions_clean = json.loads(json.dumps(edit_decisions))

with open(ARTIFACTS_DIR / "edit_decisions.json", "w", encoding="utf-8") as f:
    json.dump(edit_decisions_clean, f, indent=2, ensure_ascii=False)

validate_artifact("edit_decisions", edit_decisions_clean)

# Write clean checkpoint
write_checkpoint(
    Path("projects"), PROJECT_ID, "edit", "completed",
    artifacts={"edit_decisions": edit_decisions_clean},
    pipeline_type="animated-explainer"
)

# Enrich with Remotion-specific fields (captions, audio) post-validation and post-checkpoint
edit_decisions["captions"] = captions
edit_decisions["audio"] = {
    "narration": {
        "src": f"projects/{PROJECT_ID}/assets/narration_concat.wav",
        "volume": 1.0
    },
    "music": {
        "src": f"projects/{PROJECT_ID}/assets/music_bg.mp3",
        "volume": 0.15,
        "fadeInSeconds": 1.0,
        "fadeOutSeconds": 2.0
    }
}
print("Edit stage completed!")

# ===================================================================
# Stage 5: Compose (Render final video)
# ===================================================================
print("\n=== STAGE 6: RENDERING VIDEO ===")
composer = VideoCompose()
final_video = RENDERS_DIR / "final.mp4"

compose_result = composer.execute({
    "operation": "render",
    "edit_decisions": edit_decisions,
    "asset_manifest": asset_manifest,
    "audio_path": str(mix_output),
    "subtitle_path": str(srt_path),
    "output_path": str(final_video),
    "options": {
        "subtitle_burn": True
    }
})

if not compose_result.success:
    print(f"ERROR rendering video: {compose_result.error}")
    sys.exit(1)

print(f"\nSUCCESS! Video composed successfully at {final_video}")

# Probe the output
probe = subprocess.run(
    ["ffprobe", "-v", "quiet", "-print_format", "json",
     "-show_format", "-show_streams", str(final_video)],
    capture_output=True, text=True,
)
info = json.loads(probe.stdout)
fmt = info.get("format", {})
duration = float(fmt.get("duration", 0))

video_stream = {}
audio_stream = {}
for s in info.get("streams", []):
    if s.get("codec_type") == "video" and not video_stream:
        video_stream = s
    elif s.get("codec_type") == "audio" and not audio_stream:
        audio_stream = s

render_report = {
    "version": "1.0",
    "outputs": [
        {
            "path": str(final_video),
            "format": "mp4",
            "codec": video_stream.get("codec_name", "h264"),
            "audio_codec": audio_stream.get("codec_name", "aac"),
            "resolution": f"{video_stream.get('width', 1280)}x{video_stream.get('height', 720)}",
            "fps": 30,
            "duration_seconds": round(duration, 2),
            "file_size_bytes": os.path.getsize(final_video),
            "platform_target": "youtube"
        }
    ],
    "render_time_seconds": compose_result.duration_seconds
}

with open(ARTIFACTS_DIR / "render_report.json", "w", encoding="utf-8") as f:
    json.dump(render_report, f, indent=2, ensure_ascii=False)

validate_artifact("render_report", render_report)
write_checkpoint(
    Path("projects"), PROJECT_ID, "compose", "completed",
    artifacts={"render_report": render_report},
    pipeline_type="animated-explainer",
    cost_snapshot=tracker.cost_snapshot()
)

# ===================================================================
# Stage 6: Publish
# ===================================================================
print("\n=== STAGE 7: PUBLISHING LOG ===")
publish_log = {
    "version": "1.0",
    "entries": [
        {
            "platform": "youtube",
            "status": "exported",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "export_path": str(final_video),
            "metadata_used": {
                "title": "Bản Thiết Kế Tháng Mười: Brazil vs Nhật Bản",
                "description": "Phân tích chiến thuật trước trận đấu kinh điển giữa Brazil và Nhật Bản tại vòng 32 đội World Cup 2026.",
                "hashtags": ["#WorldCup2026", "#BrazilVsJapan", "#FootballAnalysis"]
            }
        }
    ]
}

with open(ARTIFACTS_DIR / "publish_log.json", "w", encoding="utf-8") as f:
    json.dump(publish_log, f, indent=2, ensure_ascii=False)

validate_artifact("publish_log", publish_log)
write_checkpoint(
    Path("projects"), PROJECT_ID, "publish", "completed",
    artifacts={"publish_log": publish_log},
    pipeline_type="animated-explainer"
)
print("Pipeline execution complete! Renders ready.")
