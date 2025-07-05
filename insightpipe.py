import os, time, yaml, datetime
from analyzer import analyze_image
from publisher import publish
from utils import is_file_stable
from tagger import tag_image
from shutil import move, copy2
import argparse
import sys
# Parse CLI arguments
parser = argparse.ArgumentParser(
    description="Run InsightPipe with optional config and runtime overrides"
)

parser.add_argument("--config", default="config.yaml", help="Path to config file")
parser.add_argument("--watch_dir", help="Folder to monitor for new images")
parser.add_argument("--model_name", help="Local Ollama model to use")
parser.add_argument("--prompt", help="Prompt used in description mode")
parser.add_argument("--keywords", action="store_true", help="Enable keywording mode")
parser.add_argument("--keyword_prompt", help="Prompt for keyword generation")
parser.add_argument("--output_dir", help="Directory to save processed images")
parser.add_argument("--output_mode", choices=["copy", "move"], help="File handling mode")
parser.add_argument("--dry_run", action="store_true", help="Show final config and skip execution")

args = parser.parse_args()

# Load config from file
with open(args.config) as f:
    config = yaml.safe_load(f)

# Override with CLI args if provided
if args.watch_dir:
    config["watch_dir"] = args.watch_dir
if args.model_name:
    config["model_name"] = args.model_name
if args.prompt:
    config["prompt"] = args.prompt
if args.keywords:
    config["keywords"] = True
if args.keyword_prompt:
    config["keywordPrompt"] = args.keyword_prompt
if args.output_dir:
    config["output_dir"] = args.output_dir
if args.output_mode:
    config["output_mode"] = args.output_mode
if args.dry_run:
    print("\n🧪 InsightPipe Dry Run — Final Configuration:\n")
    for k, v in config.items():
        print(f"  {k}: {v}")
    sys.exit(0)



processed = set()
while True:
    for fname in os.listdir(config["watch_dir"]):
        fpath = os.path.join(config["watch_dir"], fname)
        default_prompt = "Describe people, animals or vehicles in this image. Do not offer to do anything else."
        model = config["model_name"]
        keywords = config.get("keywords", False)
        prompt = config.get("keywordPrompt") if keywords else config.get("prompt", default_prompt)
        if fpath in processed or not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        if is_file_stable(fpath, config["stabilization_interval"]):
            desc = analyze_image(fpath, model, config["ollama_url"], prompt)
            print(f"Processed: {fpath} -> {desc}")
            timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")

            # Decide output directory
            output_dir = config.get("output_dir", "").strip()
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                target_path = os.path.join(output_dir, fname)
                mode = config.get("output_mode", "copy").lower()
                if mode == "move":
                    move(fpath, target_path)
                else:
                    copy2(fpath, target_path)
            else:
                target_path = fpath  # default: use original location

            tag_image(target_path, desc, model, timestamp, prompt, keywords)
            publish(target_path, desc, model, prompt)

            processed.add(fpath)
    time.sleep(config["poll_interval"])
