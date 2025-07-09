import os, time, yaml, datetime
from analyzer import analyze_image
from publisher import publish
from utils import is_file_stable
from tagger import tag_image
from shutil import move, copy2, copy
import argparse
import sys
import subprocess
_config = {}
_model = None
_keyword_prompt = None
_ollama_url = None
_initialized = False
def init_from_file(config_path="config.yaml"):
    global _config, _model, _keyword_prompt, _ollama_url, _initialized
    with open(config_path, "r") as f:
        _config = yaml.safe_load(f)
    _model = _config.get("model_name")
    _keyword_prompt = _config.get("keywordPrompt")
    _ollama_url = _config.get("ollama_url")
    _initialized = True

def get_available_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split("\n")
        models = [line.split()[0] for line in lines if line.strip()]
        return models
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to retrieve models: {e}")
        return []

def generate_tag_json(fpath, desc, model, timestamp, prompt, use_keywords,max_keywords=None):
    tags = {
        "filepath": fpath,
        "timestamp": timestamp,
        "model": model,
        "keywords": []
        
    }

    if use_keywords:
        raw_keywords = [kw.strip() for kw in desc.split(",")]
        if max_keywords and isinstance(max_keywords, int):
            raw_keywords = raw_keywords[:max_keywords]
        tags["keywords"] = raw_keywords
    else:
        tags["description"] = desc

    return tags

def keyword_file(fpath, model=None,max_keywords=None):
    global _initialized

    if not _initialized:
        init_from_file()

    selected_model = model if model else _model
    available_models = get_available_models()
    if selected_model not in available_models:
        raise ValueError(f"🚫 Model '{selected_model}' not available. Choose from: {available_models}")
    timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")

    desc = analyze_image(fpath, selected_model, _ollama_url, _keyword_prompt)
    return generate_tag_json(fpath, desc, selected_model, timestamp, _keyword_prompt, True,max_keywords)
def describe_file(fpath, prompt, model=None):
    timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")

    if not _initialized:
        init_from_file()

    selected_model = model if model else _model
    available_models = get_available_models()
    if selected_model not in available_models:
        raise ValueError(f"🚫 Model '{selected_model}' not available. Choose from: {available_models}")


    desc = analyze_image(fpath, selected_model, _ollama_url, prompt)

    return {
        "filepath": fpath,
        "timestamp": timestamp,
        "model": selected_model,
        "description": desc.strip()
    }



def run_main_pipeline():

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
    parser.add_argument("--mqtt_topic", help="Base topic for MQTT publishing (overrides config)")
    parser.add_argument("--input", type=str, help="Path to image file for single-file mode")
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
    if args.mqtt_topic:
        config["mqtt_topic"] = args.mqtt_topic

    if args.watch and args.batch:
        print("⚠️ Conflicting flags: both --watch and --batch passed. Defaulting to watch mode.")

    model=config["model_name"]
    prompt = config["prompt"]
    keywords=config["keywords"]
    mqtt_topic = config.get("mqtt_topic", "insightpipe")  # Default topic if not set in config

    def validate_runtime(config, dry_run=False):
        errors = []

        # Check model availability
        model_name = config.get("model_name")
        available_models = get_available_models()
        if dry_run:
            print("[AVAILABLE MODELS]:\n", "\n* ".join(available_models))
            if args.dry_run:
                print("\n🧪 InsightPipe Dry Run — Final Configuration:\n")
            for k, v in config.items():
                print(f"  {k}: {v}")
        

        if model_name not in available_models:
            errors.append(f"Model '{model_name}' is not available via Ollama.")

        # Check MQTT topic syntax (optional example)
        topic = config.get("mqtt_topic")
        if not topic or "/" not in topic:
            errors.append(f"MQTT topic '{topic}' is malformed or missing a slash.")

        # Check paths
        watch_dir = config.get("watch_dir")
        if not os.path.exists(watch_dir):
            errors.append(f"Watch directory '{watch_dir}' does not exist.")

        # Report and bail if errors
        if errors:
            print("[CONFIG VALIDATION ERRORS]")
            for err in errors:
                print(f"  • {err}")
            sys.exit(1)
        if dry_run:
            sys.exit(0)
        
    processed= set()  # Track processed files to avoid duplicates
    validate_runtime(config, dry_run=args.dry_run)
    def process_watch_dir_loop():
        print("🔄 Watch mode enabled — monitoring folder for new images")
        while True:
            process_new_files()
            time.sleep(config["poll_interval"]) # Poll interval





    def process_watch_dir_once():
        print("🧪 Batch mode — processing all images in watch folder and subfolders")

        image_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff"]
        
        for root, dirs, files in os.walk(config["watch_dir"]):
            for f in files:
                if any(f.lower().endswith(ext) for ext in image_extensions):
                    filepath = os.path.join(root, f)
                    process_image(filepath)

        print("✅ Batch processing complete.")
        sys.exit(0)

    def process_image(fpath):
        prompt = config.get("keywordPrompt") if keywords else config.get("prompt")
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
        publish(target_path, desc, model, prompt,mqtt_topic)

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
                        copy(fpath, target_path)
                else:
                    target_path = fpath  # default: use original location

                tag_image(target_path, desc, model, timestamp, prompt, keywords)
                publish(target_path, desc, model, prompt)

                processed.add(fpath)
    if args.watch or config.get("watch", False):
        while True:
            process_watch_dir_loop()
    elif args.batch:
        process_watch_dir_once()
        sys.exit(0)
    elif args.input:
        process_image(args.input)
        sys.exit(0)
    else:
        print("🚨 No mode selected. Use --input, --batch, or --watch.")
        sys.exit(1)
if __name__ == "__main__":
    # your CLI argument parsing and execution goes here
    run_main_pipeline()



   
  
