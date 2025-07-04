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
        if fpath in processed or not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        if is_file_stable(fpath, config["stabilization_interval"]):
            desc = analyze_image(fpath, config["model_name"], config["ollama_url"])
            print(f"Processed: {fpath} -> {desc}")
            timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            tag_image(fpath, desc, config["model_name"], timestamp)
            publish(fpath, desc, config["model_name"])
            processed.add(fpath)
    time.sleep(config["poll_interval"])
