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
parser.add_argument("--keyword_prompt", help="Prompt for keyword generation")
parser.add_argument("--output_dir", help="Directory to save processed images")
parser.add_argument("--output_mode", choices=["copy", "move"], help="File handling mode")
parser.add_argument("--dry_run", action="store_true", help="Show final config and skip execution")
parser.add_argument("--watch", action="store_true", help="Enable watch mode for continuous tagging")
parser.add_argument("--keywords", action="store_true", help="Enable keywording mode")
parser.add_argument("--no_keywords", action="store_true", help="Disable keywording mode")
parser.add_argument("--batch", action="store_true", help="Distable watch, enable batch processing of existing images")

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
if args.keyword_prompt:
    config["keywordPrompt"] = args.keyword_prompt
if args.output_dir:
    config["output_dir"] = args.output_dir
if args.output_mode:
    config["output_mode"] = args.output_mode
if args.keywords:
    config["keywords"] = True
elif args.no_keywords:
    config["keywords"] = False
if args.watch:
    config["watch"] = True
if args.batch:
    config["watch"] = False

if args.watch and args.batch:
    print("⚠️ Conflicting flags: both --watch and --batch passed. Defaulting to watch mode.")

if args.dry_run:
    print("\n🧪 InsightPipe Dry Run — Final Configuration:\n")
    for k, v in config.items():
        print(f"  {k}: {v}")
    sys.exit(0)
model=config["model_name"]
prompt = config["prompt"]
keywords=config["keywords"]
processed= set()  # Track processed files to avoid duplicates
def process_watch_dir_loop():
    print("🔄 Watch mode enabled — monitoring folder for new images")
    while True:
        process_new_files()
        time.sleep(config["poll_interval"]) # Poll interval





def process_watch_dir_once():
    print("🧪 Batch mode — processing all images in watch folder once")

    image_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff"]
    files = [
        f for f in os.listdir(config["watch_dir"])
        if any(f.lower().endswith(ext) for ext in image_extensions)
    ]

    for filename in files:
        filepath = os.path.join(config["watch_dir"], filename)
        process_image(filepath)
    print("✅ Batch processing complete.")
    sys.exit(0)

def process_image(fpath):
    desc = analyze_image(fpath, model, config["ollama_url"], prompt)
    print(f"Processed: {fpath} -> {desc}")
    timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")

    # Decide output directory
    output_dir = config.get("output_dir", "").strip()
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        target_path = os.path.join(output_dir, fpath.split(os.path.sep)[-1])  # Keep original filename
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




def process_new_files():
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
if args.watch or config.get("watch", False):
    while True:
        process_watch_dir_loop()
else:
    process_watch_dir_once()
    sys.exit(0)



   
  
