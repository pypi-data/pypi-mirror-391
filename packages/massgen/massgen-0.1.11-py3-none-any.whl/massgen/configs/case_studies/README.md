# Case Study Generation Configs

This directory contains configurations for automated case study generation workflows.

## Available Configs

### `case_study_generator.yaml`
**Full automated case study generation**

Creates comprehensive case studies including:
- Analysis of new features from CHANGELOG
- Demo config design
- Terminal recording
- Video editing (speed up to 1-1.5min)
- Caption generation
- Complete case study documentation

**Usage:**
```bash
# Run with embedded prompt (NEW!)
uv run massgen --config massgen/configs/case_studies/case_study_generator.yaml

# Or override the prompt
uv run massgen --config massgen/configs/case_studies/case_study_generator.yaml "Create case study for v0.2.0"
```

The prompt is embedded in the config - no need to specify it!

**Features:**
- ✅ Embedded prompt in config file
- ✅ Task planning enabled for organized workflow
- ✅ Auto-quits when complete (skip_agent_selector)
- ✅ High reasoning effort for complex analysis
- ✅ All video tools integrated

**Tools used:**
- `run_massgen_with_recording` - Terminal recording with VHS
- `understand_video` - Video analysis with GPT-4.1
- `speed_up_video` - FFmpeg-based video speed adjustment
- `generate_captions` - SRT/VTT caption generation
- MCP filesystem tools - File read/write

**Output:**
- `docs/source/examples/case_studies/v{version}_{feature}.md` - Case study doc
- `massgen/configs/case_studies/v{version}_demo.yaml` - Demo config
- `workspace_case_study/massgen_terminal_speed*.mp4` - Edited video
- `workspace_case_study/*.srt`, `*.vtt` - Caption files

---

### `video_workflow.yaml`
**Video generation only (no case study writing)**

Focused on creating demo videos with editing and captions.

**Usage:**
```bash
uv run massgen --config massgen/configs/case_studies/video_workflow.yaml
```

Agent will ask you:
- Which config to demo
- What question to use
- Target video length

Then automatically:
1. Records terminal session
2. Analyzes video
3. Speeds up to target length
4. Generates captions
5. Provides final files

**Output:**
- `workspace_video/massgen_terminal.mp4` - Original recording
- `workspace_video/massgen_terminal_speed*.mp4` - Edited video
- `workspace_video/*.srt`, `*.vtt` - Captions

---

## Prerequisites

### Required
- **VHS terminal recorder**: `brew install vhs`
- **FFmpeg**: `brew install ffmpeg`
- **OpenAI API key**: In `.env` file

### Optional
- **MCP video-audio server**: For advanced editing features

## Example Workflow

**Generating a case study for v0.1.9:**

```bash
# Full case study generation
uv run massgen --config massgen/configs/case_studies/case_study_generator.yaml
```

The agent will:
1. Read CHANGELOG.md to find v0.1.9 features
2. Design a demo config
3. Record the demo running
4. Edit video to 1.5 minutes
5. Add captions
6. Write case study doc
7. Save all artifacts

**Just creating a demo video:**

```bash
# Video only
uv run massgen --config massgen/configs/case_studies/video_workflow.yaml
```

Agent asks for config and question, then creates edited, captioned video.

## Video Editing Tips

### Speed Calculation
To condense a video to target length:

```
speed_factor = original_duration / target_duration
```

Examples:
- 10min → 1.5min: `speed_factor = 600 / 90 = 6.67`
- 5min → 1.5min: `speed_factor = 300 / 90 = 3.33`
- 3min → 1min: `speed_factor = 180 / 60 = 3.0`

### Caption Guidelines
- 10-15 captions for 1-1.5min videos
- Technical style for feature demos
- Descriptive style for tutorials
- Both SRT and VTT for maximum compatibility

## Directory Structure

```
massgen/configs/case_studies/
├── README.md (this file)
├── case_study_generator.yaml
├── video_workflow.yaml
└── v{version}_demo.yaml (generated demo configs)

docs/source/examples/case_studies/
└── v{version}_{feature}.md (generated case studies)

workspace_case_study/
├── massgen_terminal.mp4 (original recording)
├── massgen_terminal_speed6.67x.mp4 (edited video)
├── massgen_terminal_speed6.67x.srt (captions)
└── massgen_terminal_speed6.67x.vtt (captions)
```

## See Also

- **Case Study Template**: `docs/source/examples/case_studies/case-study-template.md`
- **Terminal Evaluation Guide**: `docs/source/user_guide/terminal_evaluation.rst`
- **Writing Configs Guide**: `docs/source/development/writing_configs.rst`
