import os, time, yaml, datetime
from analyzer import analyze_image
from publisher import publish
from utils import is_file_stable
from tagger import tag_image
from shutil import move, copy2

with open("config.yaml") as f:
    config = yaml.safe_load(f)

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
