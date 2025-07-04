# InsightPipe

InsightPipe is a lightweight, configurable vision analysis pipeline built for local image classification using Ollama-hosted LLMs. It monitors a directory for new images, generates descriptions, and publishes metadata via MQTT.

## Features
- File stabilization check (safe for SMB/NFS shares)
- Vision model inference (via Ollama)
- MQTT publishing with model context
- Config-driven architecture

## Requirements
- Python 3.10+
- Ollama with a vision-capable model (e.g., `llava`)
- ExifTool installed
