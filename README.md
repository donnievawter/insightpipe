# InsightPipe

![Local LLM Powered](https://img.shields.io/badge/LLM-local-orange?style=flat-square)
![Offline First](https://img.shields.io/badge/Mode-offline-blue?style=flat-square)
![Flexible Pipeline](https://img.shields.io/badge/Design-modular-success?style=flat-square)

> 🧠 LLM-powered image classification — offline, modular, and camera-agnostic

**InsightPipe** decouples image analysis from camera infrastructure, letting you classify, tag, and broadcast image events from any source using flexible LLM inference. It’s designed for post-processing output from tools like Frigate, but doesn’t rely on their internal models or formats.

---

## 🔒 Local Model Support

### 🧠 Private LLM Inference (No Cloud Required)

InsightPipe connects to local models via [Ollama](https://ollama.com), giving you full control over:

- ✅ What model is used  
- ✅ What prompt is passed  
- ✅ Where results are stored or sent

This allows you to run fully offline pipelines—no external API calls, no image uploads, no cloud dependencies.

Models are served locally using `ollama run`, and you can easily swap between different models like:

```
ollama run gemma ollama run openhermes
```

If your workflow demands **zero cloud contact**, InsightPipe is built for you.

---

## 🔧 Key Features

- Prompt-driven detection using local LLMs
- Modular pipeline for scan → analyze → tag → publish
- Supports reprocessing with multiple models and prompts
- Metadata tagging (IPTC/XMP) for tools like Adobe Bridge, Photoshop, Immich
- MQTT broadcasting for downstream event integration
- Configurable output directories and file handling (move/copy)

---

## 📐 Architecture Overview

![InsightPipe Architecture](assets/arch.jpg)


---

## 🚀 Getting Started

```
git clone https://github.com/donnievawter/insightpipe cd insightpipe python3 -m venv venv-insight source venv-insight/bin/activate pip install -r requirements.txt
```

Update `config.yaml` and `.env` with your preferred model, prompt, watch directory, and output settings.

---

## 🛠 Configuration

`config.yaml`
```
watch_dir: /Volumes/wildlife 
model_name: gemma-3b
prompt: Describe people, animals or vehicles in this image...
output_dir: /Volumes/processed 
output_mode: copy 
ollama_url: http://localhost:11434
poll_interval: 3 
stabilization_interval: 2
```
`.env`
```
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USER=username
MQTT_PASSWORD=passwor
MQTT_TOPIC=wildlife/insightpipe

```
---
## Requirements
- Python 3.10+
- Ollama with a vision-capable model (e.g., `llava`)
- ExifTool installed

---

## 🌱 Philosophy

InsightPipe was designed to remain general. It doesn’t presume what image came from which source, doesn’t embed camera logic, and doesn’t enforce classifier formats. This lets you extend it across:

- Wildlife tracking  
- Security camera systems  
- Social media event prepping  
- Batch inference for archival images

Think of it not as a plugin, but a flexible bridge from perception to insight.

---

## 🏷️ Semantic Keywording Mode

Starting in `v1.3`, InsightPipe supports **prompt-driven keyword extraction**, making it even easier for non-coders to auto-tag images for search, cataloging, or archival use.

### 🔀 Configuration

Enable keyword mode by setting these fields in `config.yaml`:

```yaml
keyword: true
keywordPrompt: What keywords would best describe this image? Provide a comma-separated list of tags...
```

- When `keyword: true`, the app uses `keywordPrompt` instead of the main `prompt`
- Output is written to `IPTC:Keywords`, not to `Description`
- No prompt metadata is stored, keeping tags clean and lean

### ✅ Benefits

- Works with **local LLMs via Ollama**
- Generates highly relevant, searchable tags
- Ideal for workflows in **photo archiving, semantic search, or gallery prep**
- No coding required—just drop images into the watch folder and go

---

---

## 🧠 Command-Line Execution

Starting in `v1.4`, InsightPipe supports runtime overrides via command-line flags, making it easy to launch multiple instances, test alternative configs, or integrate with shell workflows.

### 🔧 Available Flags

```bash
python insightpipe.py [flags]

--config            Path to YAML config file (default: config.yaml)
--watch_dir         Folder to monitor for new images
--model_name        Ollama model to use for inference
--prompt            Prompt for description mode
--keyword           Enable keywording mode
--keyword_prompt    Prompt for keyword extraction
--output_dir        Folder to save processed images
--output_mode       File handling method: copy or move
--dry_run           Show final config after overrides and exit
```

### 🔄 Example Usage

```bash
python insightpipe.py \
  --watch_dir /Volumes/wildlife \
  --output_dir /Volumes/tagged \
  --model_name gemma:3b \
  --keyword \
  --keyword_prompt "Provide a comma-separated list of animal descriptors"
```

Use `--dry_run` to inspect final configuration before execution:

```bash
python insightpipe.py --config custom.yaml --dry_run
```

---

