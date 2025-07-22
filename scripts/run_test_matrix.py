#!/usr/bin/env python3

import subprocess
import yaml
import os
import re
from glob import glob
from itertools import product
from datetime import datetime
import shutil

# 📍 Anchor paths to project root (parent of this script)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 🗂️ File locations
MODEL_FILE   = os.path.join(PROJECT_ROOT, "assets", "models.txt")
PROMPT_FILE  = os.path.join(PROJECT_ROOT, "assets", "prompts.yaml")
IMAGE_FOLDER = os.path.join(PROJECT_ROOT, "assets", "test_images")
OUTPUT_ROOT  = os.path.join(PROJECT_ROOT, "results")

# 🧠 Slug generator for filenames & folders
def slugify(text: str) -> str:
    return re.sub(r'\W+', '-', text.lower()).strip('-')

# 🧮 Load models
with open(MODEL_FILE) as f:
    models = [
        line.strip()
        for line in f
        if line.strip() and not line.strip().startswith("#")
    ]

# 🧾 Load prompts (support both flat list or dict["prompts"])
with open(PROMPT_FILE) as f:
    data = yaml.safe_load(f)
    prompts = data["prompts"] if isinstance(data, dict) and "prompts" in data else data

# 🖼️ Load images
images = sorted(glob(os.path.join(IMAGE_FOLDER, "*.*")))

# 🕒 Timestamped run ID for folder grouping
run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
import shutil

TEMP_DIR = os.path.join(PROJECT_ROOT, "temp_batch")
os.makedirs(TEMP_DIR, exist_ok=True)

...

for model_name, prompt, image_path in product(models, prompts, images):
    # 🧹 Clean temp folder
    for f in os.listdir(TEMP_DIR):
        os.remove(os.path.join(TEMP_DIR, f))

    # 🖼️ Copy target image into temp folder
    shutil.copy(image_path, TEMP_DIR)

    # 🔧 Slug setup
    prompt_slug = slugify(prompt)
    model_slug  = slugify(model_name)
    output_dir  = os.path.join(OUTPUT_ROOT, run_id, model_slug, prompt_slug)
    os.makedirs(output_dir, exist_ok=True)

    # 🚀 CLI command
    cmd = [
        "python3", os.path.join(PROJECT_ROOT, "insightpipe.py"),
        "--config", os.path.join(PROJECT_ROOT, "config.yaml"),
        "--watch_dir", TEMP_DIR,
        "--model_name", model_name,
        "--prompt", prompt,
        "--output_dir", output_dir,
        "--output_mode", "copy",
        "--no_keywords",  
        "--mqtt_topic", "insightpipe/testresults",  # Default topic for batch runs
        "--batch"
    ]

    print(f"🚀 Running → {model_name} | {prompt_slug} | {os.path.basename(image_path)}")
    subprocess.run(cmd)
