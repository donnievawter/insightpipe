import os, time, yaml
from analyzer import analyze_image
from publisher import publish
from utils import is_file_stable
from tagger import tag_image
import datetime

with open("config.yaml") as f:
    config = yaml.safe_load(f)

processed = set()
while True:
    for fname in os.listdir(config["watch_dir"]):
        fpath = os.path.join(config["watch_dir"], fname)
        prompt = config.get("prompt", "What do you see in this image?")
        model= config["model_name"]
        if fpath in processed or not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        if is_file_stable(fpath, config["stabilization_interval"]):
            desc = analyze_image(fpath, model, config["ollama_url"],prompt)
            print(f"Processed: {fpath} -> {desc}")
            timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            tag_image(fpath, desc, model, timestamp,prompt)
            publish(fpath, desc, model,prompt)
            processed.add(fpath)
    time.sleep(config["poll_interval"])
